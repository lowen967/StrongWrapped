from django.shortcuts import render, redirect
import pandas as pd
import numpy as np
import os
from .forms import UploadFileForm

def handle_uploaded_file(f):
    with open('uploaded_file.csv', 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

def demo(request):
    return render(request, 'demo.html')

def upload_file(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = request.FILES['file']
            file_name, file_extension = os.path.splitext(uploaded_file.name)
            if file_extension.lower() != '.csv':
                return redirect('error')

            handle_uploaded_file(uploaded_file)

            df = pd.read_csv('uploaded_file.csv')

            df['Weight'] = np.where(df['Exercise Name'].str.endswith('(Dumbbell)'), df['Weight'] * 2, df['Weight'])
            df['Weight'] = np.where(df['Exercise Name'].str.endswith('(Assisted)'), df['Weight'] - df['Weight'], df['Weight'])
            df['Total Weight'] = df['Weight'] * df['Reps']
            total_weight_lifted = round(df['Total Weight'].sum())

            most_frequent_exercise = df['Exercise Name'].mode()[0]
            most_frequent_count = df['Exercise Name'].value_counts().iloc[0]

            total_sets = len(df)
            total_reps = df['Reps'].sum()

            percent_most_frequent = round((most_frequent_count / total_sets) * 100)
            total_reps_most_frequent = df[df['Exercise Name'] == most_frequent_exercise]['Reps'].sum()
            percent_reps_most_frequent = round((total_reps_most_frequent / total_reps) * 100)
            total_weight_lifted_most_frequent = round(df[df['Exercise Name'] == most_frequent_exercise]['Total Weight'].sum())
            percent_weight_most_frequent = round((total_weight_lifted_most_frequent / total_weight_lifted) * 100)

            highest_weight_entry = round(df['Weight'].max())
            corresponding_exercise = df.loc[df['Weight'].idxmax(), 'Exercise Name']

            def calculate_avg_set_order(series):
                filtered_series = []
                for i in range(len(series) - 1):
                    if series.iloc[i] >= series.iloc[i + 1]:
                        filtered_series.append(series.iloc[i])
                if series.iloc[-1] >= series.iloc[-2]:
                    filtered_series.append(series.iloc[-1])
                return round(np.mean(filtered_series), 2) 

            avg_set_order = calculate_avg_set_order(df['Set Order'])
            
            mean_reps = round(df[df['Reps'] != 0]['Reps'].mean(), 2)
            mean_weight = round(df[df['Weight'] != 0]['Weight'].mean(), 2)

            request.session['total_weight_lifted'] = int(total_weight_lifted)
            request.session['most_frequent_exercise'] = most_frequent_exercise
            request.session['most_frequent_count'] = int(most_frequent_count)
            request.session['total_sets'] = int(total_sets)
            request.session['total_reps'] = int(total_reps)
            request.session['percent_most_frequent'] = int(percent_most_frequent)
            request.session['total_reps_most_frequent'] = int(total_reps_most_frequent)
            request.session['total_weight_lifted_most_frequent'] = int(total_weight_lifted_most_frequent)
            request.session['percent_reps_most_frequent'] = int(percent_reps_most_frequent)
            request.session['percent_weight_most_frequent'] = int(percent_weight_most_frequent)
            request.session['highest_weight_entry'] = int(highest_weight_entry)
            request.session['corresponding_exercise'] = corresponding_exercise
            request.session['avg_set_order'] = avg_set_order
            request.session['mean_reps'] = mean_reps 
            request.session['mean_weight'] = mean_weight

            return redirect('results')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})

def error_page(request):
    return render(request, 'error.html', {'error_message': 'Invalid file format. Please upload a CSV file.'})

def results(request):
    total_weight_lifted = round(request.session.get('total_weight_lifted', 0))
    most_frequent_exercise = request.session.get('most_frequent_exercise', '')
    most_frequent_count = request.session.get('most_frequent_count', 0)
    total_sets = request.session.get('total_sets', 0)
    total_reps = request.session.get('total_reps', 0)
    percent_most_frequent = round(request.session.get('percent_most_frequent', 0))
    total_reps_most_frequent = request.session.get('total_reps_most_frequent', 0)
    total_weight_lifted_most_frequent = round(request.session.get('total_weight_lifted_most_frequent', 0))
    percent_reps_most_frequent = round(request.session.get('percent_reps_most_frequent', 0))
    percent_weight_most_frequent = round(request.session.get('percent_weight_most_frequent', 0))
    highest_weight_entry = request.session.get('highest_weight_entry', 0)
    corresponding_exercise = request.session.get('corresponding_exercise', '')
    avg_set_order = request.session.get('avg_set_order', 0)
    mean_reps = request.session.get('mean_reps', 0)
    mean_weight = request.session.get('mean_weight', 0)  

    context = {
        'total_weight_lifted': total_weight_lifted,
        'most_frequent_exercise': most_frequent_exercise,
        'most_frequent_count': most_frequent_count,
        'total_sets': total_sets,
        'total_reps': total_reps,
        'percent_most_frequent': percent_most_frequent,
        'total_reps_most_frequent': total_reps_most_frequent,
        'total_weight_lifted_most_frequent': total_weight_lifted_most_frequent,
        'percent_reps_most_frequent': percent_reps_most_frequent,
        'percent_weight_most_frequent': percent_weight_most_frequent,
        'highest_weight_entry': highest_weight_entry,
        'corresponding_exercise': corresponding_exercise,
        'avg_set_order': avg_set_order,
        'mean_reps': mean_reps,  
        'mean_weight': mean_weight,
    }
    return render(request, 'results.html', context)
