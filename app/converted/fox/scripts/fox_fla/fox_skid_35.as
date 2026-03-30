package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_skid_35 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_skid_35()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (parent && SSF2API.isReady() && this.self && this.self.isCPU())
            {
                if ((this.self.getCPUAction() < 10) && (this.self.getCPUAction() > 0) && (this.self.getCPULevel() >= 7))
                {
                    SSF2API.print("Crouch Cancel");
                    this.self.endAttack("crouch");
                };
            };
        }

        internal function frame5():*
        {
            this.self.endAttack();
        }


    }
}

