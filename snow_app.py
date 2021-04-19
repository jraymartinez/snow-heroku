from pycaret.classification import load_model, predict_model
import streamlit as st
import pandas as pd
import numpy as np

# Reads in saved classification model
model = load_model('predict_resolution_time')

def predict(model, input_df):
    predictions_df = predict_model(estimator=model, data=input_df)
    predictions = predictions_df['Label'][0]
    return predictions

def run():

    st.write("""
    # SNOW Resolution Time Prediction App
    This app predicts the **Resolution Time Interval**!
    """)

    st.sidebar.header('User Input Features')

    st.sidebar.markdown("""
    [Example CSV input file](https://raw.githubusercontent.com/jraymartinez/snow-heroku/main/example_input_file.csv)
    """)

    # Collects user input features into dataframe
    uploaded_file = st.sidebar.file_uploader("Upload your input CSV file", type=["csv"])
    if uploaded_file is not None:
        input_df = pd.read_csv(uploaded_file)
        input_df['group'] = input_df['business_service'].map(str) + ' | ' + input_df['service_offering'].map(str) + ' | ' + input_df['assignment_group'].map(str)
        input_display = input_df.copy()
        input_df.drop(input_df.columns[[2, 3, 4]], axis=1, inplace=True)
        input_display.drop(input_display.columns[[5]], axis=1, inplace=True)
    else:
        def user_input_features():
            contact_type = st.sidebar.selectbox('Contact Type',('Chat','Self-sevice','Integration','Email', 'Phone','Virtual Agent'
                                                                'Walk-in','Conversion', 'Alert'
                                                                ))
            category = st.sidebar.selectbox('Category',('Performance','Software','SAP APP',
                                                        'Personal Computer','Access','Password Reset','SAP Security /SAP Access',
                                                        'Analytics','Application','Server','Infrastructure alert'
                                                        ))
            business_service = st.sidebar.selectbox('Business Service',('Enterprise Server Computing','Backup and Recovery','Event Management',
                                                                        'Messaging','User Insight','ERP Access Management','T&E',
                                                                        'ERP Development','Data Platform Technologies'
                                                                        ))
            service_offering = st.sidebar.selectbox('Service Offering',('Server Offerings','Backup Offering','ServiceNow Event Management',
                                                                        'Outlook/Email offerings','Nexthink 6.26 PROD CORP INT','SAP Access Management','SAP ERP (BRP) 6 PROD HBT HBT',
                                                                        'INFORMATICA 25.0.3.2 PROD SPS HIS','SAP ECC (ERP) ECC 6.0 PROD CORP HTS',
                                                                        'SAP ECC (CIP) ECC 6.0 PROD PMT PMT','CONCUR 1.0 PROD CORP INT'))
            assignment_group = st.sidebar.selectbox('Assignment Group',('DCN CIS (HON)','HCE_Buildings_Digital Operations Support',
                                                                        'Exchange Support (INC)','User Insight','SAP Security (TCS)',
                                                                        'SAP App Batch Run - HBT/SPS (NTT Data)','Analytics Batch Run','SAP App Batch Run - CORP (NTT Data)',
                                                                        'SAP App Batch Run - PMT (NTT Data)','Expense Support'))
            group = business_service + ' | ' + service_offering + ' | ' + assignment_group
            data = {'contact_type': contact_type,
                    'category': category,
                    'group': group}
            features = pd.DataFrame(data, index=[0])
            data_display = {'contact_type': contact_type,
                    'category': category,
                    'business_service': business_service,
                    'service_offering': service_offering,
                    'assignment_group': assignment_group}
            features_display = pd.DataFrame(data_display, index=[0])
            return features, features_display
        input_df, input_display = user_input_features()

    # Displays the user input features
    st.subheader('User Input features')

    if uploaded_file is not None:
        st.write(input_display)
    else:
        st.write('Awaiting CSV file to be uploaded. Currently using example input parameters (shown below).')
        st.write(input_display)

    # Apply model to make predictions
    if st.button("Predict"):
        predictions = predict(model=model, input_df=input_df)
        prediction_proba = model.predict_proba(input_df)

        st.subheader('Prediction')
        st.write(predictions)

        # Label encoded: 0: 0-1 hour, 1: 1-5 days, 2: 1-5 hours, 3: 5 hours-1day
        proba_data = {'0-1 hour': prediction_proba[0][0],
                      '1-5 hours': prediction_proba[0][2],
                      '5-24 hours': prediction_proba[0][3],
                      '1-5 days': prediction_proba[0][1]}
        st.subheader('Prediction Probability')
        st.write(pd.DataFrame(proba_data, index=[0]))

if __name__ == '__main__':
    run()