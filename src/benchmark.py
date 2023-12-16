import run_optimized
import run_noptimized
import time

querys = (
    "Hello!",
    "How are you doing?",
    "Who are you?",
    "What are you?",
    "Tell me your name.",
    "Tell me a story."
)

opt_times = []
nopt_times = []

for query in querys:
    current = time.time()

    print("Noptim: " + run_noptimized.ask(query))
    
    nopt_times.append(time.time() - current)
    
    current = time.time()

    print("Optim: " + run_optimized.ask(query))
    
    opt_times.append(time.time() - current)

opt_times_add = 0
for i in opt_times:
    opt_times_add += i
    
nopt_times_add = 0
for i in nopt_times:
    nopt_times_add += i

print(f"Optim average (sec): {opt_times_add / len(opt_times)}")
print(f"Noptim average (sec): {nopt_times_add / len(nopt_times)}")