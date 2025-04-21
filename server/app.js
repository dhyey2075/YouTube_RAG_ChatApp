const express = require('express')
const app = express()
const port = 3000
const YoutubeTranscript = require('youtube-transcript')


app.get('/', (req, res) => {
  res.send('Hello World!')
})

app.get('/getyttranscript', async(req, res) => {
    try{
        const { url } = req.query
        if (!url) {
            return res.status(400).send('Missing videoId parameter')
        }
        const trans = await YoutubeTranscript.YoutubeTranscript.fetchTranscript(url)

        let text = ""
        for(let script of trans){
            text += script.text
        }

        res.json({
            status: "Sucess",
            message: text
        })
    } catch(e){
        res.json({
            status:"Error",
            message: e.message
        })
    }
    
})

app.listen(port, () => {
  console.log(`Example app listening on port ${port}`)
})