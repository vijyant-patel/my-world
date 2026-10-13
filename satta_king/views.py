from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import DailyNumber
from .services import predict_heuristic, predict_ml, get_tens, get_ones
import json

@login_required
def dashboard(request):
    default_categories = ['DSWR', 'DLBZ', 'SRGN', 'FRBD', 'GZBD', 'GALI']
    
    order_param = request.GET.get('order')
    if order_param:
        categories = order_param.split(',')
        # Fallback for missing ones
        categories += [c for c in default_categories if c not in categories]
    else:
        categories = default_categories
    
    
    timings = {
        'DSWR': {'moti': '1.30', 'last': '4.00'},
        'DLBZ': {'moti': '2.10', 'last': '3.00'},
        'SRGN': {'moti': '3.50', 'last': '4.30'},
        'FRBD': {'moti': '5.00', 'last': '5.50'},
        'GZBD': {'moti': '8.00', 'last': '9.30'},
        'GALI': {'moti': '10.15', 'last': '11.30'},
    }
    
    # Defaults
    predict_count = int(request.GET.get('predict_count', 53))
    tens_ones_count = int(request.GET.get('tens_ones_count', 5))
    validation_rows = int(request.GET.get('validation_rows', 10))
    model_type = request.GET.get('model_type', 'HEURISTIC')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_number':
            index_str = request.POST.get('index_num')
            category = request.POST.get('category')
            number_str = request.POST.get('number')
            
            if index_str and category and number_str:
                DailyNumber.objects.update_or_create(
                    index_num=int(index_str),
                    category=category,
                    defaults={'number': int(number_str)}
                )
        return redirect('satta_dashboard')

    # Group records by index to build the list properly (aligned by index_num)
    all_indices = list(DailyNumber.objects.values_list('index_num', flat=True).distinct().order_by('index_num'))
    data_by_cat = {cat: [] for cat in categories}
    
    for idx in all_indices:
        records = DailyNumber.objects.filter(index_num=idx)
        cat_map = {r.category: r.number for r in records}
        for cat in categories:
            if cat in cat_map:
                data_by_cat[cat].append(cat_map[cat])
            else:
                data_by_cat[cat].append(None) # Pad missing with None

    max_len = len(all_indices)
    test_start = max(0, max_len - validation_rows)

    run_prediction = request.GET.get('run_prediction') == 'true'
    validation_data = []
    predictions = {}
    
    if run_prediction:
        for i in range(test_start, max_len):
            real_index = all_indices[i]
            row = {'index': real_index, 'actuals': {}, 'num_oks': {}, 'ten_oks': {}, 'one_oks': {}, 'preds': {}}
            for cat in categories:
                actual = data_by_cat[cat][i]
                
                # History is all non-None values before index i
                history = [x for x in data_by_cat[cat][:i] if x is not None]
                
                if actual is not None and len(history) > 10:
                    if model_type == 'ML':
                        preds_num = predict_ml(history, count=predict_count)
                        preds_ten = predict_ml([get_tens(x) for x in history], count=tens_ones_count, is_digit=True)
                        preds_one = predict_ml([get_ones(x) for x in history], count=tens_ones_count, is_digit=True)
                    else:
                        from .services import predict_heuristic, predict_heuristic_digits
                        preds_num = predict_heuristic(history, count=predict_count)
                        preds_ten = predict_heuristic_digits([get_tens(x) for x in history], count=tens_ones_count)
                        preds_one = predict_heuristic_digits([get_ones(x) for x in history], count=tens_ones_count)

                    row['actuals'][cat] = f"{actual:02d}"
                    row['num_oks'][cat] = "✔" if actual in preds_num else "✘"
                    row['ten_oks'][cat] = "✔" if get_tens(actual) in preds_ten else "✘"
                    row['one_oks'][cat] = "✔" if get_ones(actual) in preds_one else "✘"
                    row['preds'][cat] = [f"{x:02d}" for x in sorted(preds_num)]
                else:
                    row['actuals'][cat] = actual if actual is not None else "-"
                    row['num_oks'][cat] = "-"
                    row['ten_oks'][cat] = "-"
                    row['one_oks'][cat] = "-"
                    row['preds'][cat] = []
            
            # Add JSON version of preds for the popup
            row['preds_json'] = json.dumps(row['preds'])
            validation_data.append(row)
            
        # Generate Future Predictions
        for cat in categories:
            records = [x for x in data_by_cat[cat] if x is not None]
            if len(records) > 10:
                if model_type == 'ML':
                    p_num = predict_ml(records, count=predict_count)
                    p_ten = predict_ml([get_tens(x) for x in records], count=tens_ones_count, is_digit=True)
                    p_one = predict_ml([get_ones(x) for x in records], count=tens_ones_count, is_digit=True)
                else:
                    from .services import predict_heuristic, predict_heuristic_digits
                    p_num = predict_heuristic(records, count=predict_count)
                    p_ten = predict_heuristic_digits([get_tens(x) for x in records], count=tens_ones_count)
                    p_one = predict_heuristic_digits([get_ones(x) for x in records], count=tens_ones_count)
                rem_num = [x for x in range(100) if x not in p_num]
                predictions[cat] = {
                    'num': [f"{x:02d}" for x in sorted(p_num)],
                    'rem': [f"{x:02d}" for x in sorted(rem_num)],
                    'ten': sorted(p_ten),
                    'one': sorted(p_one),
                    'moti': timings[cat]['moti'],
                    'last': timings[cat]['last']
                }
            else:
                predictions[cat] = None
                
    next_index = max(all_indices) + 1 if all_indices else 0

    win_rates = {}
    for cat in categories:
        total = 0
        wins = 0
        for row in validation_data:
            if cat in row['num_oks'] and row['num_oks'][cat] not in ["-", ""]:
                total += 1
                if row['num_oks'][cat] == "✔":
                    wins += 1
        win_rates[cat] = round((wins / total) * 100, 1) if total > 0 else 0

    context = {
        'categories': categories,
        'validation_data': validation_data,
        'predictions': predictions,
        'next_index': next_index,
        'timings': timings,
        'predict_count': predict_count,
        'tens_ones_count': tens_ones_count,
        'validation_rows': validation_rows,
        'model_type': model_type,
        'win_rates': win_rates
    }
    return render(request, 'satta_king/dashboard.html', context)


from django.http import JsonResponse

@login_required
def api_magic_numbers(request):
    categories = ['DSWR', 'DLBZ', 'SRGN', 'FRBD', 'GZBD', 'GALI']
    all_indices = list(DailyNumber.objects.values_list('index_num', flat=True).distinct().order_by('index_num'))
    
    data_by_index = {}
    sequence = []
    for idx in all_indices:
        records = DailyNumber.objects.filter(index_num=idx)
        cat_map = {r.category: r.number for r in records}
        row_nums = []
        for cat in categories:
            if cat in cat_map and cat_map[cat] is not None:
                val = cat_map[cat]
                row_nums.append(val)
                sequence.append(val)
        data_by_index[idx] = row_nums

    valid_indices = [idx for idx in all_indices if len(data_by_index[idx]) > 0]
    target_count = int(request.GET.get('count', 47))
    target_count = max(1, min(99, target_count))
    mode = request.GET.get('mode', 'hit') # 'hit' or 'avoid'

    def get_magic_set_fast(training_rows, k):
        if not training_rows or k <= 0:
            return set()
        num_to_rows = {n: [i for i, r in enumerate(training_rows) if n in r] for n in range(100)}
        row_lens = [len(r) for r in training_rows]
        selected = set()
        current_hits = [0] * len(training_rows)
        for _ in range(k):
            best_n = -1
            best_delta = 0
            for n in range(100):
                if n in selected:
                    continue
                delta = 0
                for i in num_to_rows[n]:
                    h = current_hits[i]
                    m = row_lens[i] - h
                    before = 1000 + m * m if h == 0 else (50 + m * m if h == 1 else m * m)
                    h_new = h + 1
                    m_new = m - 1
                    after = 50 + m_new * m_new if h_new == 1 else m_new * m_new
                    delta += (after - before)
                if delta < best_delta:
                    best_delta = delta
                    best_n = n
            if best_n == -1:
                remaining = [n for n in range(100) if n not in selected]
                if remaining:
                    best_n = remaining[0]
                else:
                    break
            selected.add(best_n)
            for i in num_to_rows[best_n]:
                current_hits[i] += 1
        return selected

    def predict_for_rows(history_rows):
        if mode == 'avoid':
            # To get K numbers that should NOT come,
            # we isolate the top (100 - K) numbers that have a chance to come,
            # and take the remaining K numbers as the safest drop/avoid numbers.
            top_k = max(1, min(99, 100 - target_count))
            top_set = get_magic_set_fast(history_rows, top_k)
            return set(range(100)) - top_set
        else:
            return get_magic_set_fast(history_rows, target_count)

    # 1. True Walk-Forward Simulation:
    # For every row, predict strictly using the history before that row
    row_validations = {}
    hits_list = []
    min_history = 10
    
    for pos, current_idx in enumerate(valid_indices):
        if pos < min_history:
            continue
        history_rows = [data_by_index[i] for i in valid_indices[:pos]]
        predicted_set = predict_for_rows(history_rows)
        
        actual_nums = data_by_index[current_idx]
        matched = [f"{x:02d}" for x in actual_nums if x in predicted_set]
        hits = len(matched)
        hits_list.append(hits)
        
        row_validations[str(current_idx)] = {
            'hits': hits,
            'matched': matched,
            'total': len(actual_nums),
            'preds': [f"{x:02d}" for x in sorted(list(predicted_set))]
        }

    # 2. Future numbers for upcoming next game using 100% available data
    all_rows = [data_by_index[i] for i in valid_indices]
    future_set = predict_for_rows(all_rows)

    zero_hits = hits_list.count(0)
    one_hits = hits_list.count(1)
    two_plus_hits = sum(1 for h in hits_list if h >= 2)
    avg_hits = sum(hits_list) / len(hits_list) if hits_list else 0

    return JsonResponse({
        'mode': mode,
        'numbers': sorted(list(future_set)),
        'never_appeared': sorted([n for n in future_set if n not in sequence]),
        'row_validations': row_validations,
        'history_length': len(sequence),
        'row_stats': {
            'zero_hits': zero_hits,
            'one_hits': one_hits,
            'two_plus_hits': two_plus_hits,
            'avg_hits': round(avg_hits, 2),
            'total_rows': len(hits_list),
        }
    })
