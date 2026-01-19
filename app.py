from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans

import subprocess

def run(cmd):
    subprocess.call(cmd, shell=True)


app = Flask(__name__)
rahul
def calculate_hearing_loss(heard_volume):
    normal_threshold = 20
    return normal_threshold - heard_volume

def insert_hearing_test(name, age, volume):
    """Insert age and volume into the hearing_test table."""
    try:
        db_name = 'database.db'
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()
        
        # Step 7: Write the SQL query to insert the data
        insert_query = '''
        INSERT INTO hearing_test (name, age, volume) VALUES (?, ?, ?);
        '''
        
        # Step 8: Execute the query with the provided parameters
        cursor.execute(insert_query, (name, age, volume))
        
        # Step 9: Commit the transaction
        conn.commit()
        print("Data inserted successfully.")

    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Step 10: Close the connection
        if conn:
            conn.close()

# Function to load data from the SQLite database
def load_data():
    conn = sqlite3.connect('database.db')
    query = "SELECT age, volume FROM hearing_test"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_message(hearing_loss):
    if hearing_loss <= 20 and hearing_loss >= 0:
        message=f"Congratulations! You have good hearing ability. Keep it up!"
    elif hearing_loss <= 0 and hearing_loss > -20:
        message=f"Your hearing loss is approximately {hearing_loss:.2f} dB. Ask others to speak slightly louder but not shout. Avoid exposure to loud noises to protect remaining hearing."
    elif hearing_loss <= -20 and hearing_loss > -40:
        message=f"Your hearing loss is approximately {hearing_loss:.2f} dB. Regular use of hearing aids or assistive devices is highly recommended. Sit close to the speaker in meetings or social settings. Use visual cues like lip reading or gestures to aid in understanding."
    elif hearing_loss <= -40 and hearing_loss > -60:
        message=f"Your hearing loss is approximately {hearing_loss:.2f} dB. Focus on non-verbal communication (body language, lip reading). Extreme caution with any exposure to loud environments, as any additional hearing loss can have a major impact."
    elif hearing_loss <= -60:
        message=f"Your hearing loss is approximately {hearing_loss:.2f} dB. If hearing aids are insufficient, cochlear implants may be the best solution for sound perception. Rely primarily on sign language, written communication, or speech-to-text apps."
    return message

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/help')
def help():
    return render_template('help.html')

@app.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if request.method == 'POST':
        age = request.form['age']
        name = request.form['name']
        volume = int(request.form.get('volume', 10))  # Default volume is 10
        response = request.form['response']

        if response == 'yes':
            hearing_loss = calculate_hearing_loss(volume)
            insert_hearing_test(name, age, volume)
            message = get_message(hearing_loss)
            return render_template('result.html', message=message, name=name, age=age, volume=volume)

        elif response == 'no':
            if volume < 100:
                volume = min(100, volume + 10)
                return render_template('assessment.html', age=age, volume=volume)
            else:
                return render_template('result2.html', message="Please consult a healthcare professional.", name=name, age=age, volume=volume)

    return render_template('assessment.html', age='', volume=10)  # Default values when page loads for the first time

@app.route('/result')
def result():
    return render_template('result.html')


@app.route('/analysis')
def analysis():
    # Load data
    data = load_data()
    
    # Prepare the data for clustering
    X = data[['age', 'volume']]
    
    # Define the number of clusters
    num_clusters = 3
    
    # Create and fit the K-means model
    kmeans = KMeans(n_clusters=num_clusters, random_state=42)
    data['cluster'] = kmeans.fit_predict(X)
    
    # Calculate average age and volume per cluster
    average_age_volume = data.groupby('cluster').agg({'age': 'mean', 'volume': 'mean'}).reset_index()
    average_age_volume.columns = ['Cluster', 'Average Age', 'Average Volume']
    
    # Create a scatter plot
    plt.figure(figsize=(10, 6))
    plt.scatter(data['age'], data['volume'], c=data['cluster'], cmap='viridis', marker='o')
    centroids = kmeans.cluster_centers_
    plt.scatter(centroids[:, 0], centroids[:, 1], c='red', s=200, alpha=0.75, label='Centroids')
    plt.title('K-means Clustering of Hearing Test Data')
    plt.xlabel('Age')
    plt.ylabel('Volume Level')
    plt.legend()
    
    # Save the plot as a PNG file
    plt.savefig('static/clustering_result.png')
    plt.close()  # Close the plot to free memory
    
    # Render the HTML template with average results
    return render_template('analysis.html', averages=average_age_volume.to_dict(orient='records'))

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0')



