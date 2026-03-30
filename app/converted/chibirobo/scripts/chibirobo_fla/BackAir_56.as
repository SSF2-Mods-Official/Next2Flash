package chibirobo_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class BackAir_56 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var dir:*;
        public var BubblePos:*;

        public function BackAir_56()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6, 6, this.frame7, 7, this.frame8, 12, this.frame13, 15, this.frame16, 16, this.frame17, 22, this.frame23);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame2():*
        {
            this.dir = 1;
            if (!this.self.isFacingRight())
            {
                this.dir = -1;
            };
            this.BubblePos = new Point((-6 * this.dir), -14);
            this.self.attachEffect("bairbubbles", {
                "x":this.BubblePos.x,
                "y":this.BubblePos.y
            });
        }

        internal function frame3():*
        {
            this.self.attachEffect("bairbubbles", {
                "x":this.BubblePos.x,
                "y":this.BubblePos.y
            });
        }

        internal function frame4():*
        {
            this.self.playAttackSound(1);
            this.self.setLandingLag(true);
            if (this.self.isFacingRight())
            {
                this.BubblePos = new Point((-5 * this.dir), -3);
            };
            this.self.attachEffect("bairbubbles", {
                "x":this.BubblePos.x,
                "y":this.BubblePos.y
            });
        }

        internal function frame5():*
        {
            this.BubblePos = new Point((-18 * this.dir), -18);
            this.self.attachEffect("bairbubbles", {
                "x":this.BubblePos.x,
                "y":this.BubblePos.y
            });
        }

        internal function frame6():*
        {
            this.self.attachEffect("global_dust_blast", {
                "x":this.self.flipX(-55),
                "y":-22,
                "parentLock":true
            });
            this.BubblePos = new Point((-48 * this.dir), -22);
            this.self.attachEffect("bairbubbles", {
                "x":this.BubblePos.x,
                "y":this.BubblePos.y
            });
        }

        internal function frame7():*
        {
            this.BubblePos = new Point((-70 * this.dir), -22);
            this.self.attachEffect("bairbubbles", {
                "x":this.BubblePos.x,
                "y":this.BubblePos.y
            });
        }

        internal function frame8():*
        {
            this.self.attachEffect("bairbubbles", {
                "x":this.BubblePos.x,
                "y":this.BubblePos.y
            });
        }

        internal function frame13():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame16():*
        {
            this.self.endAttack();
        }

        internal function frame17():*
        {
            SSF2API.print("continue");
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("chibi_DStep");
            };
        }

        internal function frame23():*
        {
            this.self.endAttack();
        }


    }
}

