fetch("books.xml")
  .then((responce) => responce.text())
  .then((xmlString) => {
    const parser = new DOMParser(); // Converting the String obtained from the xmlString to xml object since the responce.text gives a String.
    const xmlDoc = parser.parseFromString(xmlString, "application/xml");

    const books = xmlDoc.getElementsByTagName("book");

    const newISBN = document.getElementById("isbn");
    const newTitle = document.getElementById("titleInput"); 
    const newAuthor = document.getElementById("authorInput"); 
    const newpublisher = document.getElementById("publisherInput"); 
    const newYear = document.getElementById("yearInput"); 
    const newPrice = document.getElementById("priceInput"); 
    const addButton = document.getElementById("insert-book");
    const viewButton = document.getElementById("view-books"); 
    

    addButton.addEventListener('click', () => {
      const newBook = xmlDoc.createElement("book")
      const userISBN = newBook.setAttribute("isbn", newISBN.value); 
      const userTitle = xmlDoc.createElement("title"); 
      const userAuthor = xmlDoc.createElement("author"); 
      const userPublisher = xmlDoc.createElement("publisher"); 
      const userYear = xmlDoc.createElement("year"); 
      const priceElement = xmlDoc.createElement("price"); 
      
      newBook.appendChild(userTitle); 
      newBook.appendChild(userAuthor); 
      newBook.appendChild(userPublisher); 
      newBook.appendChild(userYear); 

      userTitle.textContent = newTitle.value;
      userAuthor.textContent = newAuthor.value; 
      userPublisher.textContent = newpublisher.value; 
      userYear.textContent = newYear.value; 
      priceElement.textContent = newPrice.value; 

      
      const bookStore = xmlDoc.getElementsByTagName("bookstore")[0]; 
      bookStore.appendChild(newBook); 
      console.log(xmlDoc.getElementsByTagName("book"))

      const serializer = new XMLSerializer(); 
      console.log(serializer.serializeToString(xmlDoc)); 
      

   }); 
   viewButton.addEventListener('click', () => {
    console.log(xmlDoc.getElementsByTagName("book"));
     for (let i = 0; i < books.length; i++) {
      const title = books[i].getElementsByTagName("title")[0].textContent; // The GetElementByTagName will look for the tag that has the name title and then store it in an empty object so here it is [ title = the first book's title (inside the first book there could be any title tags)]
      const author = books[i].getElementsByTagName("author")[0].textContent;
      const publisher =
        books[i].getElementsByTagName("publisher")[0].textContent;
      const year = books[i].getElementsByTagName("year")[0].textContent;
      const price = books[i].getElementsByTagName("price")[0].textContent;

      console.log("---Books" + i + 1);
      console.log("Title: " + title);
      console.log("Author: " + author);
      console.log("Publisher: " + publisher);
      console.log("Year: " + year);
      console.log("Price: " + price);
    }
   }); 
  })
  
