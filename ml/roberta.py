from transformers import pipeline
import time

print("Start")
start = time.time()
pipeline = pipeline("text-classification", model="andreas122001/roberta-wiki-detector")
end = time.time()
print(end - start)
print(pipeline("Test"))

