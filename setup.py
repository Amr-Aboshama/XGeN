from distutils.core import setup

setup(name='XGeN',
      version='1.0.0',
      description='Exam Generator from PDF or text',
      author='XGeN Team - CUFE',
      author_email='am.aboshama98@gmail.com',
      packages=['XGeN', 'XGeN.InfoExtract', 'XGeN.Preprocessor', 'XGeN.QAGen', 'XGeN.Ranker'],
      url="https://github.com/Amr-Aboshama/XGeN",
      install_requires=[
         
        'torch==1.8.1',
        'transformers==4.8.2',
        'pytorch_lightning==0.8.1',
        'sense2vec==1.0.3',
        'strsim==0.0.3',
        'six==1.13.0',
        'networkx==2.4.0',
        'numpy==1.20.2',
        'scipy==1.7.0',
        'scikit-learn==0.24.2',
        'unidecode==1.1.1',
        'future==0.18.2',
        'joblib==0.14.1',
        'spacy==2.3.5',
        'pytz==2020.1',
        'python-dateutil==2.8.1',
        'boto3==1.14.40',
        'flashtext==2.7',
        'pandas==1.1.3',
        'pdfminer',
        'nltk~=3.6.2',
        'wordsegment~=1.3.1',
        'neuralcoref~=4.0',
        'Flask==2.0.1',
        'Flask-Cors==3.0.10',
        'flask-ngrok==0.0.25'
      ]
    #   ,package_data={'XGeN': ['questgen.py', 'mcq.py', 'train_gpu.py', 'encoding.py']}
      )