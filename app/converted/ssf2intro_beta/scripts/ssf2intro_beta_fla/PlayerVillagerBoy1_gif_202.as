package ssf2intro_beta_fla
{
    import flash.display.MovieClip;

    public dynamic class PlayerVillagerBoy1_gif_202 extends MovieClip
    {

        public var changeAnimationReady:*;
        public var currentAnimation:*;
        public var rand:int;

        public function PlayerVillagerBoy1_gif_202()
        {
            super();
            addFrameScript(0, this.frame1, 40, this.frame41, 127, this.frame128, 128, this.frame129, 184, this.frame185, 185, this.frame186, 236, this.frame237);
        }

        internal function frame1():*
        {
            this.changeAnimationReady = true;
            this.currentAnimation = "idle";
            this.rand = 0;
            if (parent && SSF2API.isReady())
            {
                this.rand = (10 * SSF2API.random());
                if (this.rand >= 9)
                {
                    this.gotoAndStop("wait1");
                };
            };
        }

        internal function frame41():*
        {
            this.gotoAndStop("idle");
        }

        internal function frame128():*
        {
            this.gotoAndStop("idle");
        }

        internal function frame129():*
        {
            this.changeAnimationReady = false;
            this.currentAnimation = "ko_point";
            this.rand = (10 * SSF2API.random());
            if (this.rand >= 5)
            {
                this.gotoAndStop("sd_point");
            };
        }

        internal function frame185():*
        {
            gotoAndStop("idle");
        }

        internal function frame186():*
        {
            this.changeAnimationReady = false;
            this.currentAnimation = "sd_point";
        }

        internal function frame237():*
        {
            gotoAndStop("idle");
        }


    }
}

