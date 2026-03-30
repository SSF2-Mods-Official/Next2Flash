package ssf2intro_beta_fla
{
    import flash.display.MovieClip;

    public dynamic class TomNook_gif_201 extends MovieClip
    {

        public var changeAnimationReady:*;
        public var currentAnimation:*;
        public var rand:int;

        public function TomNook_gif_201()
        {
            super();
            addFrameScript(0, this.frame1, 42, this.frame43, 43, this.frame44, 104, this.frame105, 105, this.frame106, 168, this.frame169, 169, this.frame170, 242, this.frame243);
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
                    this.gotoAndStop("wait");
                };
            };
        }

        internal function frame43():*
        {
            this.gotoAndStop("idle");
        }

        internal function frame44():*
        {
            this.changeAnimationReady = false;
            this.currentAnimation = "wait";
        }

        internal function frame105():*
        {
            this.gotoAndStop("idle");
        }

        internal function frame106():*
        {
            this.changeAnimationReady = false;
            this.currentAnimation = "ko_point";
        }

        internal function frame169():*
        {
            this.gotoAndStop("idle");
        }

        internal function frame170():*
        {
            this.changeAnimationReady = false;
            this.currentAnimation = "sd_point";
        }

        internal function frame243():*
        {
            this.gotoAndStop("idle");
        }


    }
}

