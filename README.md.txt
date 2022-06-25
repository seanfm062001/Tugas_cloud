@http('POST', '/register')
-berfungsi untuk meregister akun dengan format json
{
"username" : "<username>"
"password" : "<password>"
}

@http('GET', '/logout')
-berfungsi untuk menghilangkan session akun 

@http('POST', '/login')
-berfungsi untuk mendapatkan session
{
"username" : "<username>"
"password" : "<password>"
}

@http('POST', '/upload')
-berfungsi untuk upload file 

@http('GET', '/download/<int:idgambar>')
--berfungsi untuk dwonload gambar dengan kepemilikan user tertentu dan juga id tertentu gambar yang dimiliki