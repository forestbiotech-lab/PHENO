/**
   * Created by Bruno Costa 28-04-2018
   * Generated by Utilities/createTable.py
   */
  'use strict';

  module.exports = function(sequelize, DataTypes) {
    const ObservationVariable = sequelize.define('ObservationVariable', {
      id: { 
        type: DataTypes.INTEGER(11),
        autoIncrement: true,
        primaryKey: true,
        allowNull: false,
        unique: true,
      },
    observationVariableId: DataTypes.STRING(254),
    name: DataTypes.STRING(50),
    ontologyId: DataTypes.INTEGER(11),
    growthStage: DataTypes.STRING(50),
    status: DataTypes.STRING(20),
    xref: DataTypes.STRING(100),
    institution: DataTypes.INTEGER(11),
    scientist: DataTypes.INTEGER(11),
    date: DataTypes.DATE,
    language: DataTypes.STRING(2),
    crop: DataTypes.INTEGER(11),
    traitId: DataTypes.INTEGER(15),
    methodId: DataTypes.INTEGER(15),
    scaleId: DataTypes.INTEGER(15),
    defaultValue: DataTypes.STRING(50),
  }, {
      tableName: 'ObservationVariable',
      timestamps: false,
      underscored: false,

     classMethods: {
        associate: function associate(models) {    
          ObservationVariable.belongsTo(models.ContextOfUse, {
            foreignKey: 'id',              //on ObservationVariable
            targetKey: 'observationVariableId',  //foreign key  
          });
          ObservationVariable.belongsTo(models.Observation, {
            foreignKey: 'id',              //on ObservationVariable
            targetKey: 'observationVariableId',  //foreign key  
          });
          ObservationVariable.belongsTo(models.Ontology, {
            foreignKey: 'ontologyId',              //on ObservationVariable
            targetKey: 'id',  //foreign key  
          });
          ObservationVariable.belongsTo(models.Institution, {
            foreignKey: 'institution',              //on ObservationVariable
            targetKey: 'id',  //foreign key  
          });
          ObservationVariable.belongsTo(models.Person, {
            foreignKey: 'scientist',              //on ObservationVariable
            targetKey: 'id',  //foreign key  
          });
          ObservationVariable.belongsTo(models.Crop, {
            foreignKey: 'crop',              //on ObservationVariable
            targetKey: 'id',  //foreign key  
          });
          ObservationVariable.belongsTo(models.Trait, {
            foreignKey: 'traitId',              //on ObservationVariable
            targetKey: 'id',  //foreign key  
          });
          ObservationVariable.belongsTo(models.Method, {
            foreignKey: 'methodId',              //on ObservationVariable
            targetKey: 'id',  //foreign key  
          });
          ObservationVariable.belongsTo(models.Scale, {
            foreignKey: 'scaleId',              //on ObservationVariable
            targetKey: 'id',  //foreign key  
          });
          ObservationVariable.belongsTo(models.ObservationVariableSynonym, {
            foreignKey: 'id',              //on ObservationVariable
            targetKey: 'observationVariableId',  //foreign key  
          });
          ObservationVariable.belongsTo(models.StudyObservationVariable, {
            foreignKey: 'id',
            targetKey: 'observationVariableId',
          })  
        }
      },
    });

    return ObservationVariable;
  };