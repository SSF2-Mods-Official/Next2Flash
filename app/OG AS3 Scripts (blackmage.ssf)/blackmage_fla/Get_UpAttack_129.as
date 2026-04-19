// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Get_UpAttack_129

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Get_UpAttack_129 extends MovieClip 
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BlackMageExt;

        public function Get_UpAttack_129()
        {
            addFrameScript(0, this.frame1, 8, this.frame9, 11, this.frame12, 13, this.frame14, 15, this.frame16, 24, this.frame25);
        }

        internal function frame1():*
        {
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

