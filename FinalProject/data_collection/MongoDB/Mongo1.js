/* {"u_id" : 1, "_id":0 } 

distinct( "u_id", {})

ISODate("2015-02-13T18:58:56.267Z")

db.Messages.find({}).limit(10)
*/

/*

*/


/* number of messages per users: Bot's u_id=1 */
db.Messages.aggregate(
   [
      {
        $group : {
           _id : "$u_id",
           count: { $sum: 1 }
        }
      },
      {
         $sort:{"count":-1}
      }
   ]
)

/* Daily message counts & unique users: without bot's messages */
db.Messages.aggregate(
   [
   	{
        $match : {
           u_id : {$gt: 1}
        }
      },
      {
        $group : {
           _id : { year: { $year: "$date" }, month: { $month: "$date" }, day: { $dayOfMonth: "$date" } },
           MessageCount: { $sum: 1 },
           Users: {$addToSet: "$u_id"}
        }
      },
      {
        $project:{
            "MessageCount" : 1,
            UsersCount:{$size:"$Users"} } 
      },
      {
         $sort:{"_id.year":1, "_id.month":1, "_id.day":1}
      }
   ]
)

db.Messages.find( 
	{ u_id: { $gt: 1 }
	},
	{u_id:1,date:{ year: { $year: "$date" }, month: { $month: "$date" }, day: { $dayOfMonth: "$date" } }, _id:0}
)

db.Messages.aggregate(
   [
   	{
        $match : {
           u_id : {$gt: 1}
        }
      },
      {
        $project:{
            "Date" : { year: { $year: "$date" }, month: { $month: "$date" }, day: { $dayOfMonth: "$date" } }
      }},
      {
         $sort:{"_id.year":1, "_id.month":1, "_id.day":1}
      }
   ]
)



db.Messages.find().limit(3)
db.Conversations.find().limit(3)

db.Messages.find().limit(3)


db.Conversations.find(
//    { 
//        'participants.0._id' : 1
//	}
).limit(3)

db.Conversations.aggregate(
   [
   	{
        $match : {
           'participants.0._id' : 1
        }
    },
//    {
//        $limit : 10
//    },
    {
        $lookup : {
            from: "Messages",
            localField: 'participants.1._id',
            foreignField: 'u_id',
            as: "messages_ddxk"
        }
    },
    {
        "$unwind" : "$messages_ddxk"
    },
    {
        $group : {
           _id : "$messages_ddxk.u_id",
           MessageCount: { $sum: 1 }
        }
    },
    {
        $project:{
            "MessageCount" : 1,
            "_id" : 1 }
      }
   ]
)
