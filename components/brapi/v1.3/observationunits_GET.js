var fmtWhereAttr = require('./../helpers/formatWhereAttribute');
var controller = require('./../controllers/callController_v1.3');
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
var callStructure = require('./../structures/v1.3/observationunits');
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

module.exports = function(options){
  var options= options || {body:{},params:{},query:{}};  
  options.where={}

//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  call="observationunits"
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  //Where logic
  //Do this for each where attribute needed.

  //missing sort and sortBy
//|||||||||||||||||studyDbId||||||||||||||  
  attribute=options.query.studyDbId
  var value=fmtWhereAttr(attribute,"in")
  if ( value != null )
    options.where.studyId=value 
  delete options.query.studyDbId;
//|||||||||||||||||commonCropName||||||||||||||
  attribute=options.query.commonCropName
  var value=fmtWhereAttr(attribute,"eq")
  if ( value != null )
    options.where["$Germplasm.Species.Crop.commonCropName$"]=value 
  delete options.query.commonCropName;
//|||||||||||||||||studyTypeDbId||||||||||||||
  attribute=options.query.studyTypeDbId
  var value=fmtWhereAttr(attribute,"eq")
  if ( value != null )
    options.where["$Study.type$"]=value 
  delete options.query.studyTypeDbId;
//|||||||||||||||||programDbId||||||||||||||
  attribute=options.query.programDbId;
  var value=fmtWhereAttr(attribute,"eq")
  if ( value != null )
    options.where["$Study.Trial.programId$"]=value 
  delete options.query.programDbId;
//|||||||||||||||||locationDbId||||||||||||||
  attribute=options.query.locationDbId
  var value=fmtWhereAttr(attribute,"eq")
  if ( value != null )
    options.where["$Study.locationId$"]=value 
  delete options.query.locationDbId;
//|||||||||||||||||seasonDbId||||||||||||||   MISSING
  attribute=options.query.seasonDbId;
  var value=fmtWhereAttr(attribute,"eq")
  if ( value != null )
    options.where["$Study.StudySeason.seasonId$"]=value 
  delete options.query.seasonDbId;
//|||||||||||||||||trialDbId||||||||||||||
  attribute=options.query.trialDbId
  var value=fmtWhereAttr(attribute,"eq")
  if ( value != null )
    options.where["$Study.trialId$"]=value 
  delete options.query.trialDbId;
//|||||||||||||||||active||||||||||||||
  attribute=options.query.active
  var value=fmtWhereAttr(attribute,"eq")
  if ( value != null )
    options.where["$Study.active$"]=value 
  delete options.query.active;
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

  return controller(options,call,callback)
  
}

function callback(res){
  //[The attribute in main table used as uniqueId]
  var attribute="id"
    //Metadata
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

    var metadata={}
//!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  return {metadata:metadata,attribute:attribute,callStructure:callStructure};
}