// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.SpotDodge_114

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class SpotDodge_114 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function SpotDodge_114()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 10, this.frame11, 13, this.frame14);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:BlackMageExt;
            if (SSF2API.isReady())
            {
                this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            };
        }

        internal function frame2():*
        {
            this.self.attachEffect("bm_misstext", {
                "flip":false,
                "resize":false
            });
            this.self.setIntangibility(true);
            this.self.attachEffect("global_dust_cloud", {
                "scaleX":0.8,
                "scaleY":0.8
            });
        }

        internal function frame11():*
        {
            this.self.setIntangibility(false);
        }

        internal function frame14():*
        {
            this.self.endAttack();
        }


    }
}//package blackmage_fla

