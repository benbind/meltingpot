import os
import time


sigma_vals = ["3", "4", "5", "6", "7"]
tax_vals = ["2", "3", "4"]

i = 1
for sigma in sigma_vals:
    for tax in tax_vals:
        cmd = (f"python SocialEnvDesign/apple_picking_game.py --track --sigma-vals {sigma} --fixed-tax {tax} > {sigma=}_{tax=}.out 2>&1")
        if i % 3 != 0:
            cmd += " &"
        print('Running command:', cmd)
        os.system(cmd)
        time.sleep(5)
        i += 1
        # if i == 4:
        #     exit(0)
# "python SocialEnvDesign/apple_picking_game.py --track --sigma-vals {sigma_vals} --fixed-tax {tax}"
