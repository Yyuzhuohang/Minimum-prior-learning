import numpy as np 
import glob
import math
from sklearn.metrics import r2_score
from sklearn.metrics import mean_squared_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import precision_recall_curve, auc
#from lifelines.utils import concordance_index
from scipy.stats import pearsonr
import torch
from torch.utils.data import Dataset, DataLoader
import matplotlib.pyplot as plt
import glob
import cv2

class CustomDataset(Dataset):
    def __init__(self, sequences1, labels):
        self.sequences1 = sequences1
        self.labels = labels
        
    def __len__(self):
        return len(self.labels)
    
    def __getitem__(self, index):
        sequence1 = self.sequences1[index]
        label = self.labels[index]
        
        return sequence1, label

class give_batch():
    def __init__(self):
        self.check_and_load()
    
    def check_and_load(self):
        self.train_x_1=[]
        self.train_y=[]
        for line in glob.glob("../2_model/data/DL.TRAIN/*"):
            for linee in glob.glob(line+'/*'):
                image = cv2.imread(linee)
                #image = cv2.resize(image, (14, 14))
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                ret,gray_image=cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
                gray_image[gray_image == 255] = 1
                #gray_image = gray_image.flatten()
                label = line.split('/')[-1].split('_')[0]
                self.train_x_1.append(gray_image)
                self.train_y.append(int(label))
        
        self.test_x_1=[]
        self.test_y=[]
        for line in glob.glob("../2_model/data/DL.TEST/*"):
            for linee in glob.glob(line+'/*'):
                image = cv2.imread(linee)
                #image = cv2.resize(image, (14, 14))
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                ret,gray_image=cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY)
                gray_image[gray_image == 255] = 1
                #gray_image = gray_image.flatten()
                label = line.split('/')[-1].split('_')[0]
                self.test_x_1.append(gray_image)
                self.test_y.append(int(label))

def c_indexx(y_true, y_pred):
    summ = 0
    pair = 0
    for i in range(1, len(y_true)):
        for j in range(0, i):
            pair += 1
            if y_true[i] > y_true[j]:
                summ += 1 * (y_pred[i] > y_pred[j]) + 0.5 * (y_pred[i] == y_pred[j])
            elif y_true[i] < y_true[j]:
                summ += 1 * (y_pred[i] < y_pred[j]) + 0.5 * (y_pred[i] == y_pred[j])
            else:
                pair -= 1

    if pair is not 0:
        return summ / pair
    else:
        return 0

def SD(y_true, y_pred):
    from sklearn.linear_model import LinearRegression
    #y_pred = y_pred.reshape((-1,1))
    #y_true = np.matrix(y_true)
    #y_true = y_true.reshape((-1,1))
    lr = LinearRegression().fit(y_pred,y_true)
    y_ = lr.predict(y_pred)
    return np.sqrt(np.square(y_true - y_).sum() / (len(y_pred) - 1))
    
def CORR(y_true, y_pred):
    return pearsonr(y_true, y_pred)[0]
        
def calculate_aupr(Y,P):
    Y_ = []
    P_ = []
    for i,j in zip(Y,P):
        if i>=7:
            i=1
        else:
            i=0
        if j>=7:
            j=1
        else:
            j=0
        Y_.append(i)
        P_.append(j)
    Y_ = np.array(Y_)
    P_ = np.array(P_)
    precision, recall, _ = precision_recall_curve(Y_, P_)
    aupr = auc(recall, precision)
    return aupr

def r_squared_error(y_obs,y_pred):
    y_obs = np.array(y_obs)
    y_pred = np.array(y_pred)
    y_obs_mean = [np.mean(y_obs) for y in y_obs]
    y_pred_mean = [np.mean(y_pred) for y in y_pred]

    mult = sum((y_pred - y_pred_mean) * (y_obs - y_obs_mean))
    mult = mult * mult

    y_obs_sq = sum((y_obs - y_obs_mean)*(y_obs - y_obs_mean))
    y_pred_sq = sum((y_pred - y_pred_mean) * (y_pred - y_pred_mean) )

    return mult / float(y_obs_sq * y_pred_sq)
    
def get_k(y_obs,y_pred):
    y_obs = np.array(y_obs)
    y_pred = np.array(y_pred)

    return sum(y_obs*y_pred) / float(sum(y_pred*y_pred))

def squared_error_zero(y_obs,y_pred):
    k = get_k(y_obs,y_pred)

    y_obs = np.array(y_obs)
    y_pred = np.array(y_pred)
    y_obs_mean = [np.mean(y_obs) for y in y_obs]
    upp = sum((y_obs - (k*y_pred)) * (y_obs - (k* y_pred)))
    down= sum((y_obs - y_obs_mean)*(y_obs - y_obs_mean))

    return 1 - (upp / float(down))

def get_rm2(ys_orig,ys_line):
    r2 = r_squared_error(ys_orig, ys_line)
    r02 = squared_error_zero(ys_orig, ys_line)

    return r2 * (1 - np.sqrt(np.absolute((r2*r2)-(r02*r02))))
        
def get_cindex(Y, P):
    summ = 0
    pair = 0
    
    for i in range(1, len(Y)):
        for j in range(0, i):
            if i is not j:
                if(Y[i] > Y[j]):
                    pair +=1
                    summ +=  1* (P[i] > P[j]) + 0.5 * (P[i] == P[j])
        
            
    if pair is not 0:
        return summ/pair
    else:
        return 0
        
def get_test_acc_regression(y,predict,name="Test==>"):
    y_ = y.cpu().numpy()
    predict_ = predict.cpu().numpy()
    #mae = mean_absolute_error(y_,predict_)
    #sd = self.SD(y_,predict_)
    #rmse = np.sqrt(mean_squared_error(y_,predict_))
    #r_score = r2_score(y_,predict_) #PCORR
    mse = mean_squared_error(y_,predict_)
    r = get_rm2(y_,predict_)
    c_index = get_cindex(y_,predict_)
    # aucpr = calculate_aupr(y_,predict_)
    
    #to_print=name+"mae: %.3f"%(mae)+'\t'+"rmse: %.3f"%(rmse)+'\t'+"R: %.3f"%(r_score)+'\t'+'\t'+"CI: %.3f"%(c_index)
    to_print=name+"mse: %.3f"%(mse)+'\t'+"CI: %.3f"%(c_index)+'\t'+"r: %.3f"%(r)#+'\t'+"aucpr: %.3f"%(aucpr)
    print(to_print)
    return to_print
    
def find_intersection(lists):
    result = []
    for i in range(len(lists[0])):
        if all(lists[j][i] > 0 for j in range(len(lists))):#593 581
            result.append(lists[0][i])#######
        else:
            result.append(0)
    return result

def plt_hist(lst,name='1'):
    plt.figure(figsize=(10, 6))
    plt.hist(lst, bins=20, color='aqua', edgecolor='black', alpha=0.3)
    
    plt.title('error', fontsize=16)
    plt.xlabel('error values', fontsize=14)
    plt.ylabel('number of error', fontsize=14)
    
    plt.tight_layout()
    plt.savefig('error_%s.png'%(name),dpi=600)
    plt.close()

def dra_fit(true_values,predicted_values):
    #slope, intercept = np.polyfit(true_values, predicted_values, 1)
    #fit_values = slope * true_values + intercept

    plt.scatter(true_values, predicted_values, label="Data Points", color='blue')
    #plt.plot(true_values, fit_values, color='red', label=f"Fit: y = {slope:.2f}x + {intercept:.2f}")

    min_val = min(min(true_values), min(predicted_values))
    max_val = max(max(true_values), max(predicted_values))
    plt.plot([min_val, max_val], [min_val, max_val], 'k--')

    plt.xlabel('True Values')
    plt.ylabel('Predicted Values')
    plt.title('True vs Predicted Values with Linear Fit')
    plt.legend()
    plt.savefig('nihe.png',dpi=600)
    plt.close()

def plt_bar(values,qujian,min_val, max_val):
    bin_size = (max_val - min_val) / qujian
    labels = [f"{min_val + i*bin_size:.2f}-{min_val + (i+1)*bin_size:.2f}" for i in range(qujian)]
    
    plt.bar(labels, values)
    plt.xlabel('Bins')
    plt.ylabel('Average Value')
    plt.title('Average relative error')
    plt.xticks(rotation=30)
    plt.tight_layout()
    plt.savefig('bar.png',dpi=600)
    plt.close()

def give_class(label_1):
    label_1 = float(label_1)
    #if label_1 >= 8.0:
    #    label_2 = 'super high'
    if label_1 >= 7.0:
        label_2 = 'high'
    elif label_1 >= 6.0:
        label_2 = 'medium'
    else:
        label_2 = 'low'
    return label_2
def saveval_file(labels,pres,name='Test'):
    with open('lav_pre_val.txt','w',encoding = 'utf-8') as w_wilf:
        for lab,pre in zip(labels,pres):
            w_wilf.write(str(lab)+'\t'+str(pre)+'\t'+name+'\n')
        w_wilf.close()
def assign_to_bins(data,pre,qujian):
    min_val, max_val = min(data), max(data)
    
    bin_size = (max_val - min_val) / qujian
    
    bins = [[] for _ in range(qujian)]
    
    for num,p in zip(data,pre):
        if num == max_val:
            index = qujian-1
        else:
            index = int((num - min_val) / bin_size)
        num_1 = (num-p)/num
        bins[index].append(num_1)
    bins = [np.mean(x) for x in bins]
    plt_bar(bins,qujian,min_val, max_val)

if __name__ == '__main__':
    D=give_batch()