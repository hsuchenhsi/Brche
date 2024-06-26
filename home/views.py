from django.shortcuts import render,get_object_or_404,redirect
from .forms import *
from django.contrib import messages
from home.models import MemberData,Product,Store
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm


# Create your views here.
def frontpage(request):
    products = Product.objects.all()
    return render(request, 'frontpage.html', {'products': products})

def logouts(reqiest):
    logout(reqiest)
    return redirect('/')

def register(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')
        password2=request.POST.get('password2')
        if password2 != password:
            msg='密碼錯誤。'
        elif username=='':
            msg='用戶名不得為空。'
        elif email=='':
            msg='郵箱不得為空。'
        elif User.objects.filter(username=username).exists():
            msg='用戶名已存在'
        else:
            user = User.objects.create_user(username=username, password=password, email=email)
            user.save()
            msg='註冊成功！請登入。'
            return redirect('login')  # Redirect to login page after successful registration
    return render(request, 'login.html', locals()) 

def logins(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, '登入成功！')
            return redirect('/')  # Replace 'home' with your home page URL
        else:
            msg='error'
            messages.error(request, '登入失敗，請檢查您的用戶名和密碼。')
    return render(request, 'login.html', locals())
 
def A01(request):
    return render(request,'A01.html')

def describe(request, product_no):
    product = get_object_or_404(Product, productNo=product_no)
    context = {
        'product': product,
    }
    return render(request, 'describe.html', context)

def A02(request):
    return render(request,'A02.html')

def order(request):
    return render(request,'order.html')


def information(request):
    errormessage = ""
    member = None
    try:
        current_member = request.user  # 获取当前登录的用户
        member = MemberData.objects.get(memberName=current_member.username)
    except MemberData.DoesNotExist:
        errormessage = " (找不到該會員的資料)"
    except Exception as e:
        errormessage = f" (讀取錯誤: {e})"
    
    memberdatas = MemberData.objects.all()  # 获取所有会员数据

    if request.method == 'POST':
        new_phone = request.POST.get('phone')
        new_email = request.POST.get('email')
        new_address = request.POST.get('address')

        if member:
            member.phone = new_phone
            member.email = new_email
            member.address = new_address
            member.save()
            messages.success(request, '資料已成功更新')
            return redirect('information')  # 重新导向到信息页面

    return render(request, 'information.html', {'memberdata': member, 'errormessage': errormessage, 'memberdatas': memberdatas})

def member(request):
    return render(request, 'member.html')

from django.contrib.auth.hashers import make_password
from .models import OrderDetail, Post

def user_login(request):
    if request.method == 'POST':
        # 處理註冊表單的提交
        username = request.POST.get('username')
        email = request.POST.get('email')
        raw_password = request.POST.get('password')
        # 加密密碼
        encrypted_password = make_password(raw_password)
        # 創建用戶對象並保存
        user = Post(username=username, email=email, password=encrypted_password)
        user.save()
        # 渲染註冊成功頁面或其他適當的回應
        return render(request, 'login.html', {'username': username})
    else:
        # GET請求，渲染註冊表單
        return render(request, 'frontpage.html')

from django.shortcuts import render, redirect
from .forms import ProductForm,StoreForm
from django.contrib import messages
def manage_products(request):
    if request.method == 'POST':
        product_form = ProductForm(request.POST)
        store_form = StoreForm(request.POST)
        if product_form.is_valid():
            product_form.save()
            messages.success(request, '新增商品成功！')
            return redirect('manage_products')
    else:
        product_form = ProductForm()
        store_form = StoreForm()


    products = Product.objects.all()
    stores = Store.objects.all()
    return render(request, 'manage_products.html', {
        'product_form': product_form,
        'store_form': store_form,
        'products': products,
        'stores': stores
    })

def delete_product(request, productNo):
    product = get_object_or_404(Product, productNo=productNo)
    if request.method == 'POST':
        product.delete()
        return redirect('manage_products')
    return render(request, 'delete_product.html', {'product': product})

def edit_product(request, productNo):
    product = get_object_or_404(Product, productNo=productNo)
    if request.method == 'POST':
        form = ProductForm(request.POST, instance=product)
        if form.is_valid():
            form.save()
            return redirect('manage_products')
    else:
        form = ProductForm(instance=product)

    return render(request, 'edit_product.html', {'form': form})


from django.conf import settings
from .forms import UploadFileForm

from import_export.fields import Field 
from django.http import HttpResponse

def upload_file(request):
    if request.method == 'POST' and request.FILES['excel_file']:
        excel_file = request.FILES['excel_file']
        # 处理您的 Excel 文件并将数据保存到数据库
        # 这里假设您使用了 pandas 来处理 Excel 文件
        import pandas as pd
        df = pd.read_excel(excel_file)
        for index, row in df.iterrows():
            if pd.isna(row['category']) or pd.isna(row['subcategory']) or pd.isna(row['name']) or pd.isna(row['description']) or pd.isna(row['photo-src']) or pd.isna(row['price']):
                # 如果有空值或nan值，跳过这一行
                continue
            #Excel讀取的資料
            Product.objects.create(
                category=row['category'],
                subcategory=row['subcategory'],
                productName=row['name'],
                describe=row['description'],
                picture=row['photo-src'],
                price=row['price']
            )
            html_content = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>上傳成功</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background-color: #f2f2f2;
                margin: 0;
            }
            .container {
                text-align: center;
                background: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #4CAF50;
            }
            button {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 5px;
                text-decoration: none;
                font-size: 16px;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #45a049;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>上傳成功</h1>
            <button onclick="location.href='/'">回首頁</button>
        </div>
    </body>
    </html>
    '''

        return HttpResponse(html_content)
    return render(request, 'upload.html')

def manage_store(request):
    if request.method == 'POST':
        store_form = StoreForm(request.POST)
        if store_form.is_valid():
            store_form.save()
            messages.success(request, '新增庫存成功！')
            return redirect('manage_store')
    else:
        store_form = StoreForm()

    stores = Store.objects.all()
    return render(request, 'manage_store.html', {
        'store_form': store_form,
        'stores': stores
    })

def delete_store(request, storeNo):
    store = get_object_or_404(Store, storeNo=storeNo)
    if request.method == 'POST':
        store.delete()
        messages.success(request, '庫存已刪除！')
        return redirect('manage_store')
    return render(request, 'delete_store.html', {'store': store})

def edit_store(request, storeNo):
    store = get_object_or_404(Store, storeNo=storeNo)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('manage_store')
    else:
        form = StoreForm(instance=store)

    return render(request, 'edit_store.html', {'store_form': form})
from django.http import JsonResponse
from .models import Store

def get_quantity(request, size):
    try:
        store_entry = Store.objects.get(size=size)
        quantity = store_entry.quantity
        return JsonResponse({'status': 'success', 'quantity': quantity})
    except Store.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Size not found in store'}, status=404)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)


def order_detail_view(request):
    order_detail = OrderDetail.objects.get(id=1)  # 假设您从数据库中获取了订单详情
    price = order_detail.quantity * order_detail.singlePrice

    context = {
        'order_detail': order_detail,
        'price': price,
    }

    return render(request, 'order.html', context)

def cart(request):
    return render(request,'cart.html')