package
{
   public class SSF2Item extends SSF2GameObject
   {
      public function SSF2Item(param1:*)
      {
         super(param1);
      }
      
      override public function getType() : String
      {
         return "SSF2Item";
      }
      
      override public function inState(param1:uint) : Boolean
      {
         if(isDisposed())
         {
            SSF2API.print("Warning: API attempted to check inState(IState." + IState.toString(param1) + ") after object has been disposed!");
            return param1 === 3;
         }
         return super.inState(param1);
      }
      
      override public function setState(param1:uint) : void
      {
         if(param1 === 3)
         {
            SSF2API.print("Warning: Cannot explicitly set SSF2Item to DEAD state. Please use destroy() method instead.");
         }
         super.setState(param1);
      }
      
      public function destroy(param1:Boolean = false) : void
      {
         _api.destroy(param1);
      }
      
      public function fireProjectile(param1:*, param2:Number = 0, param3:Number = 0, param4:Boolean = false, param5:Object = null) : *
      {
         return _api.fireProjectile(param1,param2,param3,param4,param5);
      }
      
      public function getItemStat(param1:String) : *
      {
         return _api.getItemStat(param1);
      }
      
      public function getUses() : int
      {
         return _api.getUses();
      }
      
      public function isReversed() : Boolean
      {
         return _api.isReversed();
      }
      
      public function resetTime() : void
      {
         _api.resetTime();
      }
      
      public function updateItemStats(param1:Object) : void
      {
         _api.updateItemStats(param1);
      }
      
      public function getOwner() : *
      {
         return _api.getOwner();
      }
      
      public function setOwner(param1:*) : void
      {
         _api.setOwner(param1);
      }
      
      public function getHolder() : *
      {
         return _api.getHolder();
      }
      
      public function setHolder(param1:*) : void
      {
         _api.setHolder(param1);
      }
      
      public function toIdle(param1:* = null) : void
      {
         _api.toIdle(param1);
      }
      
      public function toHeld(param1:* = null) : void
      {
         _api.toHeld(param1);
      }
      
      public function toToss(param1:* = null) : void
      {
         _api.toToss(param1);
      }
      
      public function setFrameInterrupt(param1:Function) : void
      {
         _api.setFrameInterrupt(param1);
      }
      
      public function setHurtInterrupt(param1:Function) : void
      {
         _api.setHurtInterrupt(param1);
      }
      
      public function isZDropped() : Boolean
      {
         return _api.isZDropped();
      }
   }
}

