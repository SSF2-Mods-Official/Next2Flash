package lucario_fla
{
    import flash.display.MovieClip;

    public dynamic class Crouch_77 extends MovieClip
    {

        public var aura1:MovieClip;
        public var aura2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var itemBox:MovieClip;
        public var self:LucarioExt;
        public var moving:Boolean;
        public var controls:*;

        public function Crouch_77()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 4, this.frame5, 5, this.frame6, 6, this.frame7, 8, this.frame9, 13, this.frame14, 23, this.frame24, 26, this.frame27);
        }

        public function updateCrawl():*
        {
            this.controls = this.self.getControls();
            if ((!(this.controls.LEFT) && !(this.controls.RIGHT)) || (this.controls.LEFT && this.controls.RIGHT))
            {
                this.self.destroyTimer(this.updateCrawl);
                gotoAndStop("loop");
            }
            else if ((this.self.isFacingRight() && this.controls.RIGHT) || (!(this.self.isFacingRight()) && this.controls.LEFT))
            {
                if ((currentFrame < 6) || (currentFrame >= 13))
                {
                    gotoAndStop("crawlforward");
                };
            }
            else if ((!(this.self.isFacingRight()) && this.controls.RIGHT) || (this.self.isFacingRight() && this.controls.LEFT) && (currentFrame < 14))
            {
                gotoAndStop("crawlback");
            };
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as LucarioExt);
            this.moving = false;
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateAuraPaws();
            };
        }

        internal function frame2():*
        {
            this.self.playSound("lucario_crouch");
        }

        internal function frame4():*
        {
            this.self.setGlobalVariable("crouchdown", true);
            this.moving = false;
            this.self.updateAuraPaws();
        }

        internal function frame5():*
        {
            gotoAndStop("loop");
        }

        internal function frame6():*
        {
            this.moving = true;
            this.self.createTimer(1, -1, this.updateCrawl);
        }

        internal function frame7():*
        {
            this.self.updateAuraPaws();
        }

        internal function frame9():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("lucario_step2");
            };
        }

        internal function frame14():*
        {
            gotoAndStop("crawlforward");
        }

        internal function frame24():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_step_s2");
            }
            else
            {
                this.self.playSound("lucario_step2");
            };
        }

        internal function frame27():*
        {
            gotoAndStop("crawlforward");
        }


    }
}

