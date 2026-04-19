// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Get_UpAttack_129

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpAttack_129 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function Get_UpAttack_129()
        {
            addFrameScript(0, this.frame1, 8, this.frame9, 11, this.frame12, 13, this.frame14, 15, this.frame16, 24, this.frame25);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:MovieClip;
            var _local_6:BlackMageExt;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.setIntangibility(true);
            };
        }

        internal function frame9():*
        {
            this.self.playAttackSound(1);
        }

        internal function frame12():*
        {
            this.self.attachEffect("global_dust_swirl");
        }

        internal function frame14():*
        {
            this.self.playAttackSound(2);
        }

        internal function frame16():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

