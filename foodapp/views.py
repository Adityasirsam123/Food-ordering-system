
from django.shortcuts import render, redirect
from django.db import connection, transaction
from foodapp.forms import FoodForm,CustForm,AdminForm,CartForm,OrderForm
from foodapp.models import Food,Cust,Admin,Cart,Order
import datetime
import razorpay
from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .models import Payment, Order
from .forms import OrderForm

cursor = connection.cursor()

# Create your views here.

def foodapp(request):
	return render(request,'index.html')

def addfood(request):
	if request.method=="POST":
		form = FoodForm(request.POST,request.FILES)
		if form.is_valid():
			try:
				form.save()
				return redirect("/allfood")
			except:
				return render(request,"error.html")
	else :
		form = FoodForm()
	return render(request,'addfood.html',{'form':form})
	
def showfood(request):
	foods = Food.objects.all()
	return render(request,'foodlist.html',{'foodlist':foods})
	
def deletefood(request,FoodId):
	foods = Food.objects.get(FoodId=FoodId)
	foods.delete()
	return redirect("/allfood")
	
def getfood(request,FoodId):
	foods = Food.objects.get(FoodId=FoodId)
	return render(request,'updatefood.html',{'f':foods})
	
def updatefood(request,FoodId):
	foods = Food.objects.get(FoodId=FoodId)
	form = FoodForm(request.POST,request.FILES,instance=foods)
	if form.is_valid():
		form.save()
		return redirect("/allfood")
	return render(request,'updatefood.html',{'f':foods})
	
def addcust(request):
	if request.method=="POST":
		form = CustForm(request.POST)
		if form.is_valid():
			try:
				form.save()
				return redirect("/login")
			except:
				return render(request,"error.html")
	else :
		form = CustForm()
	return render(request,'addcust.html',{'form':form})
	
def showcust(request):
	custs = Cust.objects.all()
	return render(request,'custlist.html',{'custlist':custs})

def deletecust(request,CustId):
	custs = Cust.objects.get(CustId=CustId)
	custs.delete()
	return redirect("/allcustomer")
	
def getcust(request):
	print(request.session['CustId'])
	for c in Cust.objects.raw('Select * from FP_Cust where CustEmail="%s"'%request.session['CustId']):
		custs=c
	return render(request,'updatecust.html',{'c':custs})
	
def updatecust(request,CustId):
	custs = Cust.objects.get(CustId=CustId)
	form = CustForm(request.POST,instance=custs)
	if form.is_valid():
		form.save()
		session_keys = list(request.session.keys())
		for key in session_keys:
			del request.session[key]
		return redirect("/login")
	return render(request,'updatecust.html',{'c':custs})
	
	
	
def login(request):
	return render(request,'login.html')
	
def doLogin(request):
	if request.method=="POST":
		uid = request.POST.get('userId','')
		upass = request.POST.get('userpass','')
		utype = request.POST.get('type','')
		
		if utype == "Admin":
			for a in Admin.objects.raw('Select * from FP_Admin where AdminId="%s" and AdminPass="%s"'%(uid,upass)):
				if a.AdminId==uid:
					request.session['AdminId']=uid
					return render(request,"index.html",{'success':'Welcome '+a.AdminId})
			else:
				return render(request,"login.html",{'failure':'Incorrect login details'})
					
		if utype == "User":
			for a in Cust.objects.raw('Select * from FP_Cust where CustEmail="%s" and CustPass="%s"'%(uid,upass)):
				if a.CustEmail==uid:
					request.session['CustId']=uid
					return render(request,"index.html",{'success':'Welcome '+a.CustEmail})
			else:
				return render(request,"login.html",{'failure':'Incorrect login details'})
				
def doLogout(request):
	key_session = list(request.session.keys())
	for key in key_session:
		del request.session[key]
	return render(request,'index.html',{'success':'Logged out successfully'})
	
def addcart(request,FoodId):
	sql = ' Insert into FP_Cart(CustEmail,FoodId,FoodQuant) values("%s","%d","%d")'%(request.session['CustId'],FoodId,1)
	i=cursor.execute(sql)
	transaction.commit()
	return redirect('/allfood')
	
def delcart(request,CartId):
	cart = Cart.objects.get(CartId=CartId)
	cart.delete()
	return redirect("/allcart")
	
def showcart(request):
	cart=Cart.objects.raw('Select CartId,FoodName,FoodPrice,FoodQuant,FoodImage from FP_Food as f inner join FP_Cart as c on f.FoodId=c.FoodId where c.CustEmail="%s"'%request.session['CustId'])
	transaction.commit()
	return render(request,"cartlist.html",{'cartlist':cart})
	
def updatepasswd(request):
	return render(request,'updatepasswd.html')
		
def changepass(request):
	if request.method == "POST":
		aid=request.session['AdminId']
		opss=request.POST.get('OLDPass','')
		newpss=request.POST.get('NEWPass','')
		cnewpss=request.POST.get('CONFPass','')
		for a in Admin.objects.raw('select * from FP_Admin where AdminId="%s" and AdminPass="%s"'%(aid,opss)):
			if a.AdminId == aid:
				sql = 'update FP_Admin set AdminPass="%s" where AdminId="%s"' %(newpss,request.session['AdminId'])
				i=cursor.execute(sql)
				transaction.commit()
				session_keys = list(request.session.keys())
				for key in session_keys:
					del request.session[key]
				return redirect("/login")
		else:
			return render(request,'updatepasswd.html',{'failure':'Invalid attempt.'})

def placeorder(request):
        if request.method=="POST":
                price=request.POST.getlist('FoodPrice','')
                q=request.POST.getlist('FoodQuant','')
                total=0.0
                for i in range(len(price)):
                    total=total+float(price[i])*float(q[i])
                today = datetime.datetime.now()
                sql = 'insert into FP_Order(CustEmail,OrderDate,TotalBill) values ("%s","%s","%f")' %(request.session['CustId'],today,total)
                i=cursor.execute(sql)
                transaction.commit()
                sql1= 'select * from FP_Order where CustEmail="%s" and OrderDate="%s"'%(request.session['CustId'],today)
                sql = 'delete from FP_Cart where CustEmail="%s"' %(request.session['CustId'])
                i=cursor.execute(sql)
                transaction.commit()
                
                od=Order()
                
                for o in Order.objects.raw(sql1):
                        if o.CustEmail==request.session['CustId']:
                                od=str(o.OrderId)
                                return render(request,'payment_form.html',{'success':'Order placed sucessfully!!!'+str(o.OrderId)})
        else:
        	pass

def getorder(request):
	orders = Order.objects.all()
	return render(request,'orderlist.html',{'orderlist':orders})

def updateQNT(request,s):
	print(s)
	ind=s.index('@')
	cartId=int(s[:ind])
	qt=int(s[ind+1:])
	sql="update FP_Cart set FoodQuant='%d' where CartId='%d'"%(qt,cartId)
	i=cursor.execute(sql)
	transaction.commit()
 
from django import forms
from django.http import HttpResponseBadRequest

class AmountForm(forms.Form):
    amount = forms.DecimalField(max_digits=10, decimal_places=2)

razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
from django.shortcuts import render, redirect
from django.http import HttpResponseBadRequest

def payment_view(request):
    if request.method == 'POST':
        amount_form = AmountForm(request.POST)
        order_form = OrderForm(request.POST)

        if amount_form.is_valid() and order_form.is_valid():
            order = order_form.save()
            amount = int(amount_form.cleaned_data['amount'] * 100)  # Convert to paise
            razorpay_order = razorpay_client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            })
            payment = Payment.objects.create(
                user=request.user,
                amount=amount_form.cleaned_data['amount'],
                razorpay_order_id=razorpay_order['id'],
                order=order
            )

            # Simulate a payment status check
            payment_status = (razorpay_order['id'])

            if payment_status == 'success':
                return redirect(request,'payment_success.')
            else:
                return redirect('payment_fail')
    
    return render(request, 'index.html')
               
    

"""
@csrf_exempt
def payment_callback(request):
    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id = request.POST.get('razorpay_order_id', '')
        razorpay_signature = request.POST.get('razorpay_signature', '')

        payment = Payment.objects.get(razorpay_order_id=razorpay_order_id)
        payment.razorpay_payment_id = razorpay_payment_id
        payment.razorpay_signature = razorpay_signature

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature
        }

        try:
            razorpay_client.utility.verify_payment_signature(params_dict)
            payment.success = True
            payment.save()
            return render(request, 'payment_success.html')
        except:
            payment.success = False
            payment.save()
            return render(request, 'payment-fail.html')
"""
def payment_success(request):
    return render(request, 'payment_success.html')

def payment_failure(request):
    return render(request, 'payment-fail.html')




