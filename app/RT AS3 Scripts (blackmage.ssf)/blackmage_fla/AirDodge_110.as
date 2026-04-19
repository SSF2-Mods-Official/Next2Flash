// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.AirDodge_110

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class AirDodge_110 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function AirDodge_110()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 14, this.frame15, 23, this.frame24);
        }

        public function dodgeLand(_arg_1:*=null):*
        {
            this.self.toLand();
            this.self.stancePlayFrame("dodgeland");
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
            this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.dodgeLand);
        }

        internal function frame15():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

