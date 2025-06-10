var updateBtns = document.getElementsByClassName('update-cart')


for(var i=0; i<updateBtns.length ; i++){
  	updateBtns[i].addEventListener('click', function(){
	    var productId = this.dataset.product
	    var action = this.dataset.action
	    console.log('productId: ', productId, 'action: ',action)
	    
	    console.log('USER: ', user);
	    if(user != 'AnonymousUser'){
	      	updateUserOrder(productId, action)
	    }
	    else {
	       	print('Uhuyy')
	    }
	})
}

function updateUserOrder(productId,action){
	console.log('User Is Logged In, Sending Data..')
	var url = '/update-item/'

	fetch(url, {
	    method:'POST',
	    headers:{
	      	'Content-Type':'application/json',
	      	'X-CSRFToken':csrftoken,
	    },
	    // the below 'body' is being sent as a JSON string to 'updateItem' view in views.py
	    body:JSON.stringify({'productId':productId, 'action':action})
	})
	.then((response) =>{
    	return response.json();
	})
    .then((data) =>{
	    console.log('Data:',data)
	    //below line is written, to refresh the page to increment the cart total in red on top right corner
	    location.reload()
	})
}
