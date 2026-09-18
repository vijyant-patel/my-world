from django.shortcuts import render, redirect
from .models import DailyNumber
from .services import predict_heuristic, predict_ml, get_tens, get_ones
import json

def dashboard(request):
    categories = ['DSWR', 'DLBZ', 'SRGN', 'FRBD', 'GZBD', 'GALI']
    
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

                    row['actuals'][cat] = actual
                    row['num_oks'][cat] = "✔" if actual in preds_num else "✘"
                    row['ten_oks'][cat] = "✔" if get_tens(actual) in preds_ten else "✘"
                    row['one_oks'][cat] = "✔" if get_ones(actual) in preds_one else "✘"
                    row['preds'][cat] = sorted(preds_num)
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
                    'num': sorted(p_num),
                    'rem': sorted(rem_num),
                    'ten': sorted(p_ten),
                    'one': sorted(p_one),
                    'moti': timings[cat]['moti'],
                    'last': timings[cat]['last']
                }
            else:
                predictions[cat] = None
                
    next_index = max(all_indices) + 1 if all_indices else 0

    context = {
        'categories': categories,
        'validation_data': validation_data,
        'predictions': predictions,
        'next_index': next_index,
        'timings': timings,
        'predict_count': predict_count,
        'tens_ones_count': tens_ones_count,
        'validation_rows': validation_rows,
        'model_type': model_type
    }
    return render(request, 'satta_king/dashboard.html', context)
