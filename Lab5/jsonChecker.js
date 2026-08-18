import fs from 'fs'; 
import Ajv from 'ajv'; 

fs.readFile('catalogue.schema.json', 'utf-8', (err, data) => {
    if(err){
        console.error("Couldn't find"); 
    }else{
        console.log("The file has been found")
    }

    JSON.parse(data)
    console.log(data)
}); 

