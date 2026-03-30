package ssf2intro_beta_fla
{
    import flash.display.MovieClip;

    public dynamic class Mabel_gif_203 extends MovieClip
    {

        public var changeAnimationReady:*;
        public var currentAnimation:*;
        public var rand:int;

        public function Mabel_gif_203()
        {
            super();
            addFrameScript(0, this.frame1, 40, this.frame41, 95, this.frame96, 96, this.frame97, 141, this.frame142, 142, this.frame143, 180, this.frame181);
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

        internal function frame96():*
        {
            this.gotoAndStop("idle");
        }

        internal function frame97():*
        {
            this.changeAnimationReady = false;
            this.currentAnimation = "ko_point";
            this.rand = (10 * SSF2API.random());
            if (this.rand >= 5)
            {
                this.gotoAndStop("sd_point");
            };
        }

        internal function frame142():*
        {
            gotoAndStop("idle");
        }

        internal function frame143():*
        {
            this.changeAnimationReady = false;
            this.currentAnimation = "sd_point";
        }

        internal function frame181():*
        {
            gotoAndStop("idle");
        }


    }
}

