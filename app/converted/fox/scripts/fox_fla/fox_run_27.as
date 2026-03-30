package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_run_27 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_run_27()
        {
            super();
            addFrameScript(0, this.frame1, 6, this.frame7, 11, this.frame12, 12, this.frame13, 20, this.frame21, 21, this.frame22, 25, this.frame26);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }

        internal function frame7():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s1");
            }
            else
            {
                this.self.playSound("fox_footstep");
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
                this.self.playSound("fox_footstep2");
            };
            this.self.stancePlayFrame("run");
        }

        internal function frame13():*
        {
            this.self.playSound("fox_runstart");
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
        }

        internal function frame21():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("fox_footstep");
            };
            this.self.stancePlayFrame("run");
        }

        internal function frame22():*
        {
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
            if (parent && SSF2API.isReady() && this.self && this.self.isCPU())
            {
                if ((this.self.getCPUAction() < 10) && (this.self.getCPUAction() > 0) && (this.self.getCPULevel() >= 7))
                {
                    SSF2API.print("Crouch Cancel (Turning)");
                    if (!this.self.isFacingRight())
                    {
                        this.self.importCPUControls([17408, 1, 16640, 1]);
                    }
                    else
                    {
                        this.self.importCPUControls([17408, 1, 16896, 1]);
                    };
                    this.self.endAttack("crouch");
                };
            };
        }

        internal function frame26():*
        {
            this.self.stancePlayFrame("run");
        }


    }
}

