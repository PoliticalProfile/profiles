from political_profile.celery import celery as app


@app.task(queue='sample-queue')
def sample_task(*args, **kwargs):
    print('Teste!!', args, kwargs)
