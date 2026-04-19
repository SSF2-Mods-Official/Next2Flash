// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Walk_14

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Walk_14 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function Walk_14()
        {
            addFrameScript(0, this.frame1, 4, this.frame5, 13, this.frame14, 17, this.frame18);
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

        internal function frame5():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("bm_footstep");
            };
        }

        internal function frame14():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("bm_footstep");
            };
        }

        internal function frame18():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}//package blackmage_fla

