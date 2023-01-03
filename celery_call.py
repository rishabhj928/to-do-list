from celery_code import add
x = add.delay(4,4)
print(x)