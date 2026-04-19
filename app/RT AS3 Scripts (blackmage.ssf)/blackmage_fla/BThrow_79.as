// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.BThrow_79

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class BThrow_79 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var attackBox2:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var touchBox:MovieClip;
        internal var self:BlackMageExt;
        internal var xframe:String;

        public function BThrow_79()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 5, this.frame6, 6, this.frame7, 7, this.frame8, 8, this.frame9, 23, this.frame24);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:MovieClip;
            var _local_7:MovieClip;
            var _local_8:BlackMageExt;
            var _local_9:String;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            this.xframe = null;
        }

        internal function frame3():*
        {
            SSF2API.getCamera().shake(2);
            this.self.playAttackSound(1);
        }

        internal function frame5():*
        {
            this.xframe = "attack";
        }

        internal function frame6():*
        {
            SSF2API.getCamera().shake(2);
        }

        internal function frame7():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame8():*
        {
            SSF2API.getCamera().shake(4);
        }

        internal function frame9():*
        {
            this.self.fireProjectile("bthrowrock");
        }

        internal function frame24():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

