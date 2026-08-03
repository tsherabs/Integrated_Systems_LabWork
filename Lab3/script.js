fetch("books.xml")
    .then(responce => responce.text())
    .then(xmlString => {
        const parser = new DOMParser(); // Converting the String obtained from the xmlString to xml object since the responce.text gives a String. 
        const xmlDoc = parser.parseFromString(xmlString, "application/xml"); 

        
        const books = xmlDoc.getElementsByTagName("book"); 

        for(let i = 0; i < books.length; i++){
            const title = books[i].getElementsByTagName("title")[0].textContent; // The GetElementByTagName will look for the tag that has the name title and then store it in an empty object so here it is [ title = the first book's title (inside the first book there could be any title tags)] 
            const author = books[i].getElementsByTagName("author")[0].textContent; 
            const publisher = books[i].getElementsByTagName("publisher")[0].textContent; 
            const year = books[i].getElementsByTagName("year")[0].textContent; 
            const price = books[i].getElementsByTagName("price")[0].textContent; 

            console.log("---Books" + i + 1); 
            console.log("Title: " + title); 
            console.log("Author: " + author); 
            console.log("Publisher: " + publisher); 
            console.log("Year: "  + year); 
            console.log("Price: " + price); 
        }

        
    });