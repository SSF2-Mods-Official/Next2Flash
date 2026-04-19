// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.HangAttack_118

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class HangAttack_118 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function HangAttack_118()
        {
            addFrameScript(0, this.frame1, 2, this.frame3, 9, this.frame10, 10, this.frame11, 11, this.frame12, 12, this.frame13, 24, this.frame25);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:BlackMageExt;
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

        internal function frame10():*
        {
            this.self.playSound("run_start");
        }

        internal function frame11():*
        {
            this.self.setXSpeed(8, false);
        }

        internal function frame12():*
        {
            this.self.playAttackSound(1);
            this.self.attachEffect("global_dust_light");
        }

        internal function frame13():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

