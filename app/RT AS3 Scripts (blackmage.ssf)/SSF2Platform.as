// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//SSF2Platform

package 
{
    import flash.geom.Point;

    public class SSF2Platform extends SSF2CollisionBoundary 
    {

        public function SSF2Platform(_arg_1:*):void
        {
            super(_arg_1);
        }

        override public function getType():String
        {
            return ("SSF2Platform");
        }

        public function faceRight():void
        {
            _api.faceRight();
        }

        public function faceLeft():void
        {
            _api.faceLeft();
        }

        public function setForeground(_arg_1:String):void
        {
            _api.setForeground(_arg_1);
        }

        public function getFallthrough():Boolean
        {
            return (_api.getFallthrough());
        }

        public function setFallthrough(_arg_1:Boolean):void
        {
            _api.setFallthrough(_arg_1);
        }

        public function getNoDropThrough():Boolean
        {
            return (_api.getNoDropThrough());
        }

        public function setNoDropThrough(_arg_1:Boolean):void
        {
            _api.setNoDropThrough(_arg_1);
        }

        public function getAccelFriction():Number
        {
            return (_api.getAccelFriction());
        }

        public function setAccelFriction(_arg_1:Number):void
        {
            _api.setAccelFriction(_arg_1);
        }

        public function getDecelFriction():Number
        {
            return (_api.getDecelFriction());
        }

        public function setDecelFriction(_arg_1:Number):void
        {
            _api.setDecelFriction(_arg_1);
        }

        public function getXInfluence():Number
        {
            return (_api.getXInfluence());
        }

        public function setXInfluence(_arg_1:Number):void
        {
            _api.setXInfluence(_arg_1);
        }

        public function getDanger():Boolean
        {
            return (_api.getDanger());
        }

        public function setDanger(_arg_1:Boolean):void
        {
            _api.setDanger(_arg_1);
        }

        public function getBounceSpeed():Number
        {
            return (_api.getBounceSpeed());
        }

        public function setBounceSpeed(_arg_1:Number):void
        {
            _api.setBounceSpeed(_arg_1);
        }

        public function setAlpha(_arg_1:Number):void
        {
            _api.setAlpha(_arg_1);
        }

        public function setCamFocus(_arg_1:Boolean):void
        {
            _api.setCamFocus(_arg_1);
        }

        public function getXSpeed():Number
        {
            return (_api.getXSpeed());
        }

        public function setXSpeed(_arg_1:Number):void
        {
            _api.setXSpeed(_arg_1);
        }

        public function getYSpeed():Number
        {
            return (_api.getYSpeed());
        }

        public function setYSpeed(_arg_1:Number):void
        {
            _api.setYSpeed(_arg_1);
        }

        public function getStartPosition():Point
        {
            return (_api.getStartPosition());
        }

        public function addMovement(_arg_1:Object):void
        {
            _api.addMovement(_arg_1);
        }

        public function clearMovement():void
        {
            _api.clearMovement();
        }

        public function extraHitTests(_arg_1:Number, _arg_2:Number, _arg_3:*):Boolean
        {
            return (false);
        }

        public function addIgnoreObject(_arg_1:*):void
        {
            _api.addIgnoreObject(_arg_1);
        }

        public function removeIgnoreObject(_arg_1:*):void
        {
            _api.removeIgnoreObject(_arg_1);
        }

        public function setIgnoreObjectListInversed(_arg_1:Boolean):void
        {
            _api.setIgnoreObjectListInversed(_arg_1);
        }

        public function getConserveHorizontalMomentum():Boolean
        {
            return (_api.getConserveHorizontalMomentum());
        }

        public function setConserveHorizontalMomentum(_arg_1:Boolean):void
        {
            _api.setConserveHorizontalMomentum(_arg_1);
        }

        public function getConserveUpwardMomentum():Boolean
        {
            return (_api.getConserveUpwardMomentum());
        }

        public function setConserveUpwardMomentum(_arg_1:Boolean):void
        {
            _api.setConserveUpwardMomentum(_arg_1);
        }

        public function getConserveDownwardMomentum():Boolean
        {
            return (_api.getConserveDownwardMomentum());
        }

        public function setConserveDownwardMomentum(_arg_1:Boolean):void
        {
            _api.setConserveDownwardMomentum(_arg_1);
        }


    }
}//package 

