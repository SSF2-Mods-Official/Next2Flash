// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.DodgeRoll_109

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class DodgeRoll_109 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;
        internal var effect:*;

        public function DodgeRoll_109()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 8, this.frame9, 15, this.frame16);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:BlackMageExt;
            var _local_4:*;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
        }

        internal function frame2():*
        {
            this.effect = this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.8,
                "scaleY":0.8
            });
            this.effect.scaleX = -(this.effect.scaleX);
        }

        internal function frame3():*
        {
            this.self.setIntangibility(true);
        }

        internal function frame9():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

