N = 137524771864208156028430259349934309717
p1_true = 37084900000000000001
p2_true = 370849000000000000037

best_p_candidate = 11727095627827384320

abs_distance_p1 = abs(best_p_candidate - p1_true)
abs_distance_p2 = abs(best_p_candidate - p2_true)

min_abs_distance = min(abs_distance_p1, abs_distance_p2)

rel_distance = min_abs_distance / min(p1_true, p2_true)

print(f"Min Absolute Distance: {min_abs_distance}")
print(f"Relative Distance: {rel_distance}")