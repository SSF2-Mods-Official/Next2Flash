package
{
   public class SSF2Projectile extends SSF2GameObject
   {
      public function SSF2Projectile(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2Projectile";
      }
      
      override public function inState(param1:uint) : Boolean
      {
         if(isDisposed())
         {
            SSF2API.print("Warning: API attempted to check inState(PState." + PState.toString(param1) + ") after object has been disposed!");
            return param1 === 1;
         }
         return super.inState(param1);
      }
      
      override public function setState(param1:uint) : void
      {
         if(param1 === 1)
         {
            SSF2API.print("Warning: Cannot explicitly set SSF2Projectile to DEAD state. Please use destroy() method instead.");
         }
         super.setState(param1);
      }
      
      public function angleControl(param1:Number, param2:Number) : void
      {
         _api.angleControl(param1,param2);
      }
      
      public function destroy(param1:* = null) : void
      {
         _api.destroy(param1);
      }
      
      public function endControl() : void
      {
         _api.endControl();
      }
      
      public function exportStats() : Object
      {
         return _api.exportStats();
      }
      
      public function getProjectileStat(param1:String) : *
      {
         return _api.getProjectileStat(param1);
      }
      
      public function isReversed() : Boolean
      {
         return _api.isReversed();
      }
      
      public function updateProjectileStats(param1:Object) : void
      {
         _api.updateProjectileStats(param1);
      }
      
      public function getOwner() : *
      {
         return _api.getOwner();
      }
      
      public function setOwner(param1:*) : void
      {
         _api.setOwner(param1);
      }
   }
}

