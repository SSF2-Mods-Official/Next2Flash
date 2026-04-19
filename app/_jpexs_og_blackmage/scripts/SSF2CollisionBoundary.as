package
{
   import flash.display.MovieClip;
   import flash.geom.Rectangle;
   
   public class SSF2CollisionBoundary extends SSF2BaseAPIObject
   {
      public function SSF2CollisionBoundary(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2CollisionBoundary";
      }
      
      public function getOwnStats() : Object
      {
         return {};
      }
      
      public function getMC() : MovieClip
      {
         return _api.getMC();
      }
      
      public function destroy() : void
      {
         _api.destroy();
      }
      
      public function getX() : Number
      {
         return _api.getX();
      }
      
      public function setX(param1:Number) : void
      {
         _api.setX(param1);
      }
      
      public function getY() : Number
      {
         return _api.getY();
      }
      
      public function setY(param1:Number) : void
      {
         _api.setY(param1);
      }
      
      public function hitTestPoint(param1:Number, param2:Number, param3:Boolean = true) : Boolean
      {
         return _api.hitTestPoint(param1,param2,param3);
      }
      
      public function hitTestRect(param1:Rectangle, param2:Boolean = true) : Boolean
      {
         return _api.hitTestRect(param1,param2);
      }
   }
}

