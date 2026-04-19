// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Sleep_124

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Sleep_124 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function Sleep_124()
        {
            addFrameScript(0, this.frame1, 19, this.frame20);
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:MovieClip;
            var _local_4:BlackMageExt;
            this.self = (SSF2API.getCharacter(this) as BlackMageExt);
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.attachEffect("BM_Zz", {
                    "x":this.self.flipX(10),
                    "y":-26
                });
                this.self.setGlobalVariable("jab", false);
                this.self.clearEffectsOnStateChange();
            };
            if ((((parent) && (SSF2API.isReady())) && (this.self)))
            {
                this.self.playSound("fall_asleep");
            };
        }

        internal function frame20():*
        {
            this.self.stancePlayFrame("again");
        }


    }
}//package blackmage_fla

