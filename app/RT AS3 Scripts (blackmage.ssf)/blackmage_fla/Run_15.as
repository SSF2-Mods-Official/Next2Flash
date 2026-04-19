// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.Run_15

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class Run_15 extends MovieClip 
    {

        internal var hitBox:MovieClip;
        internal var hitBox2:MovieClip;
        internal var hitBox3:MovieClip;
        internal var itemBox:MovieClip;
        internal var self:BlackMageExt;

        public function Run_15()
        {
            addFrameScript(0, this.frame1, 3, this.frame4, 6, this.frame7, 7, this.frame8, 11, this.frame12, 15, this.frame16, 19, this.frame20);
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
            if (((parent) && (SSF2API.isReady())))
            {
                this.self.playSound("run_start");
            };
        }

        internal function frame4():*
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

        internal function frame7():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame8():*
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

        internal function frame12():*
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

        internal function frame16():*
        {
            this.self.stancePlayFrame("run");
        }

        internal function frame20():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("blackmage_landLight");
            };
        }


    }
}//package blackmage_fla

