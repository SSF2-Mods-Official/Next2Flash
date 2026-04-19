// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.HangClimb_116

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class HangClimb_116 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function HangClimb_116()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 8, this.frame9, 10, this.frame11, 15, this.frame16, 16, this.frame17);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame3():*
        {
            this.self.playSound("bm_doublejump");
        }

        internal function frame9():*
        {
            this.self.setXSpeed(4.5, false);
        }

        internal function frame11():*
        {
            this.self.playSound("blackmage_landLight");
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame17():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

