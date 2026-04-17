// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Item

package 
{
    public class SSF2Item extends SSF2GameObject 
    {

        public function SSF2Item(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2Item");
        }

        override public function inState(_arg_1:uint):Boolean
        {
            if (isDisposed())
            {
                SSF2API.print((("Warning: API attempted to check inState(IState." + IState.toString(_arg_1)) + ") after object has been disposed!"));
                return (_arg_1 === 3);
            };
            return (super.inState(_arg_1));
        }

        override public function setState(_arg_1:uint):void
        {
            if ((_arg_1 === 3))
            {
                SSF2API.print("Warning: Cannot explicitly set SSF2Item to DEAD state. Please use destroy() method instead.");
            };
            super.setState(_arg_1);
        }

        public function destroy(_arg_1:Boolean=false):void
        {
            _api.destroy(_arg_1);
        }

        public function fireProjectile(_arg_1:*, _arg_2:Number=0, _arg_3:Number=0, _arg_4:Boolean=false, _arg_5:Object=null):*
        {
            return (_api.fireProjectile(_arg_1, _arg_2, _arg_3, _arg_4, _arg_5));
        }

        public function getItemStat(_arg_1:String):*
        {
            return (_api.getItemStat(_arg_1));
        }

        public function getUses():int
        {
            return (_api.getUses());
        }

        public function isReversed():Boolean
        {
            return (_api.isReversed());
        }

        public function resetTime():void
        {
            _api.resetTime();
        }

        public function updateItemStats(_arg_1:Object):void
        {
            _api.updateItemStats(_arg_1);
        }

        public function getOwner():*
        {
            return (_api.getOwner());
        }

        public function setOwner(_arg_1:*):void
        {
            _api.setOwner(_arg_1);
        }

        public function getHolder():*
        {
            return (_api.getHolder());
        }

        public function setHolder(_arg_1:*):void
        {
            _api.setHolder(_arg_1);
        }

        public function toIdle(_arg_1:*=null):void
        {
            _api.toIdle(_arg_1);
        }

        public function toHeld(_arg_1:*=null):void
        {
            _api.toHeld(_arg_1);
        }

        public function toToss(_arg_1:*=null):void
        {
            _api.toToss(_arg_1);
        }

        public function setFrameInterrupt(_arg_1:Function):void
        {
            _api.setFrameInterrupt(_arg_1);
        }

        public function setHurtInterrupt(_arg_1:Function):void
        {
            _api.setHurtInterrupt(_arg_1);
        }

        public function isZDropped():Boolean
        {
            return (_api.isZDropped());
        }


    }
}//package 

