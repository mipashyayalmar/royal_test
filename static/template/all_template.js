
// console.log({{request.user.id}});
if (localStorage.getItem('cart') == null) {
    var cart = {};
    
} else {
    cart = JSON.parse(localStorage.getItem('cart'));
    updateCart(cart);
}

// If the add to cart button is clicked, add/increment the item
$('.divpr').on('click', 'button.cart', function() {
    var idstr = this.id.toString();
    //console.log(idstr);
    if (cart[idstr] != undefined) {
        qty = cart[idstr][0] + 1;
    } else {
        qty = 1;
        name = document.getElementById('name'+idstr).innerHTML;
        price = document.getElementById('price'+idstr).innerHTML;
        cart[idstr] = [qty, name, parseInt(price)];
    }
    updateCart(cart);
});


$('#popcart').popover();
updatePopover(cart);

function updatePopover(cart) {
    var popStr = "";
    popStr = popStr + "<div class='mx-2 my-2'>";
    var i = 1;
    var j = 0;
    for(var item in cart) {
        popStr = popStr + "<b>" + i + "</b>. ";
        popStr = popStr + document.getElementById('name' + item).innerHTML.slice(0, 15) + "... (Qty: " + cart[item][0] + ')<br>';
        i = i + 1;
        j = j + 1;
    }
    if(j == 0) {
        popStr = popStr + "<p><b> No item available in your cart </b></p><div class='mx-2 my-2'>";
        popStr = popStr + "</div> <a href='/shop'><button class='btn btn-primary'>Add items</button></a> ";
    }
    else{
        popStr = popStr + "</div> <a href='/shop/checkout'><button class='btn btn-primary' id='checkout'>Checkout</button></a> <a href='/shop/'><button class='btn btn-primary' onclick='clearCart()' id='clearCart'>Clear Cart</button></a>  ";
    }
    document.getElementById("popcart").setAttribute('data-content', popStr);
    $('#popcart').popover();
}

function clearCart() {
  cart = JSON.parse(localStorage.getItem('cart'));
  for (var item in cart) {
    document.getElementById('div' + item).innerHTML = '<button id="'+ item +'" class="btn btn-primary cart">Add to Cart</button>'
  }
  localStorage.clear();
  cart = {};
  updateCart(cart);
}

function updateCart(cart) {
    //console.log(cart);
    var sum = 0;
    for (var item in cart) {
        sum = sum + cart[item][0];
        document.getElementById('div' + item).innerHTML = "<button id='minus" + item + "' class='btn btn-primary minus'>-</button> <span id='val" + item + "''>" + cart[item][0] + "</span> <button id='plus" + item + "' class='btn btn-primary plus'> + </button>";
    }
    localStorage.setItem('cart', JSON.stringify(cart));
    document.getElementById('cart').innerHTML = sum;
    updatePopover(cart);
}

$('.divpr').on("click", "button.minus", function() {
    //console.log("minus clicked");
    a = this.id.slice(7, );
    cart['pr' + a][0] = cart['pr' + a][0] - 1;
    cart['pr' + a][0] = Math.max(0, cart['pr' + a][0]);
    if(cart['pr' + a][0] == 0) {
        document.getElementById('divpr' + a).innerHTML = '<button id="pr'+a+'" class="btn btn-primary cart">Add to Cart</button>';
        delete cart['pr'+a];
    }
    else {
        document.getElementById('valpr' + a).innerHTML = cart['pr' + a][0];
    }
    updateCart(cart);

});

$('.divpr').on("click", "button.plus", function() {
    //console.log("plus clicked");
    a = this.id.slice(6, );
    cart['pr' + a][0] = cart['pr' + a][0] + 1;
    document.getElementById('valpr' + a).innerHTML = cart['pr' + a][0];
    updateCart(cart);
});
