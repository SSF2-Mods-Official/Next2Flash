package
{
   import flash.geom.Point;
   
   public class SSF2Platform extends SSF2CollisionBoundary
   {
      public function SSF2Platform(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2Platform";
      }
      
      public function faceRight() : void
      {
         _api.faceRight();
      }
      
      public function faceLeft() : void
      {
         _api.faceLeft();
      }
      
      public function setForeground(param1:String) : void
      {
         _api.setForeground(param1);
      }
      
      public function getFallthrough() : Boolean
      {
         return _api.getFallthrough();
      }
      
      public function setFallthrough(param1:Boolean) : void
      {
         _api.setFallthrough(param1);
      }
      
      public function getNoDropThrough() : Boolean
      {
         return _api.getNoDropThrough();
      }
      
      public function setNoDropThrough(param1:Boolean) : void
      {
         _api.setNoDropThrough(param1);
      }
      
      public function getAccelFriction() : Number
      {
         return _api.getAccelFriction();
      }
      
      public function setAccelFriction(param1:Number) : void
      {
         _api.setAccelFriction(param1);
      }
      
      public function getDecelFriction() : Number
      {
         return _api.getDecelFriction();
      }
      
      public function setDecelFriction(param1:Number) : void
      {
         _api.setDecelFriction(param1);
      }
      
      public function getXInfluence() : Number
      {
         return _api.getXInfluence();
      }
      
      public function setXInfluence(param1:Number) : void
      {
         _api.setXInfluence(param1);
      }
      
      public function getDanger() : Boolean
      {
         return _api.getDanger();
      }
      
      public function setDanger(param1:Boolean) : void
      {
         _api.setDanger(param1);
      }
      
      public function getBounceSpeed() : Number
      {
         return _api.getBounceSpeed();
      }
      
      public function setBounceSpeed(param1:Number) : void
      {
         _api.setBounceSpeed(param1);
      }
      
      public function setAlpha(param1:Number) : void
      {
         _api.setAlpha(param1);
      }
      
      public function setCamFocus(param1:Boolean) : void
      {
         _api.setCamFocus(param1);
      }
      
      public function getXSpeed() : Number
      {
         return _api.getXSpeed();
      }
      
      public function setXSpeed(param1:Number) : void
      {
         _api.setXSpeed(param1);
      }
      
      public function getYSpeed() : Number
      {
         return _api.getYSpeed();
      }
      
      public function setYSpeed(param1:Number) : void
      {
         _api.setYSpeed(param1);
      }
      
      public function getStartPosition() : Point
      {
         return _api.getStartPosition();
      }
      
      public function addMovement(param1:Object) : void
      {
         _api.addMovement(param1);
      }
      
      public function clearMovement() : void
      {
         _api.clearMovement();
      }
      
      public function extraHitTests(param1:Number, param2:Number, param3:*) : Boolean
      {
         return false;
      }
      
      public function addIgnoreObject(param1:*) : void
      {
         _api.addIgnoreObject(param1);
      }
      
      public function removeIgnoreObject(param1:*) : void
      {
         _api.removeIgnoreObject(param1);
      }
      
      public function setIgnoreObjectListInversed(param1:Boolean) : void
      {
         _api.setIgnoreObjectListInversed(param1);
      }
      
      public function getConserveHorizontalMomentum() : Boolean
      {
         return _api.getConserveHorizontalMomentum();
      }
      
      public function setConserveHorizontalMomentum(param1:Boolean) : void
      {
         _api.setConserveHorizontalMomentum(param1);
      }
      
      public function getConserveUpwardMomentum() : Boolean
      {
         return _api.getConserveUpwardMomentum();
      }
      
      public function setConserveUpwardMomentum(param1:Boolean) : void
      {
         _api.setConserveUpwardMomentum(param1);
      }
      
      public function getConserveDownwardMomentum() : Boolean
      {
         return _api.getConserveDownwardMomentum();
      }
      
      public function setConserveDownwardMomentum(param1:Boolean) : void
      {
         _api.setConserveDownwardMomentum(param1);
      }
   }
}

