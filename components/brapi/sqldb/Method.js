/**
   * Created by Bruno Costa 28-04-2018
   * Generated by Utilities/createTable.py
   */
  'use strict';

  module.exports = function(sequelize, DataTypes) {
    const Method = sequelize.define('Method', {
      id: { 
        type: DataTypes.INTEGER(11),
        autoIncrement: true,
        primaryKey: true,
        allowNull: false,
        unique: true,
      },
    methodId: DataTypes.STRING(40),
    name: DataTypes.STRING(254),
    class: DataTypes.STRING(50),
    description: DataTypes.STRING,
    formula: DataTypes.STRING(200),
    reference: DataTypes.STRING(254),
    ontologyId: DataTypes.INTEGER(11),
  }, {
      tableName: 'Method',
      timestamps: false,
      underscored: false,

     classMethods: {
        associate: function associate(models) {    
          Method.belongsTo(models.Ontology, {
            foreignKey: 'ontologyId',              //on Method
            targetKey: 'id',  //foreign key  
          });
          Method.belongsTo(models.ObservationVariable, {
            foreignKey: 'id',              //on Method
            targetKey: 'methodId',  //foreign key
          }); 
        }
      },
    });

    return Method;
  };