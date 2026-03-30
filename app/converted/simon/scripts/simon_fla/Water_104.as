package simon_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class Water_104 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var self:*;
        public var loopStart:Boolean;
        public var maxLandLoops:*;
        public var landLoops:*;
        public var maxMoveLoops:*;
        public var moveLoops:*;
        public var fromAir:*;
        public var owner:*;

        public function Water_104()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 4, this.frame5, 8, this.frame9, 12, this.frame13, 23, this.frame24, 32, this.frame33, 42, this.frame43, 52, this.frame53, 69, this.frame70, 71, this.frame72, 72, this.frame73, 73, this.frame74);
        }

        public function ground(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.ground);
            this.self.playSound("ssf2_snd_sfx_simon_dspec_break");
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            SSF2API.getCamera().shake(6);
            this.self.updateAttackBoxStats(1, {"priority":-1});
            this.self.stancePlayFrame("land");
        }

        public function wall(_arg_1:*=null):*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point(this.self.getX(), (this.self.getY() - 30)), new Point(this.self.getX(), (this.self.getY() - 40)), {"ignoreFallthrough":true}))
            {
                if (this.self.getYSpeed() < -12)
                {
                    this.self.stancePlayFrame("roof");
                    this.self.playSound("ssf2_snd_sfx_simon_dspec_break");
                    this.self.setXSpeed(0);
                    this.self.setYSpeed(0);
                    SSF2API.getCamera().shake(6);
                    this.self.updateProjectileStats({"gravity":0});
                };
            }
            else
            {
                this.self.stancePlayFrame("wall");
                this.self.playSound("ssf2_snd_sfx_simon_dspec");
                this.self.setXSpeed(0);
                this.self.setYSpeed(0);
                SSF2API.getCamera().shake(6);
                this.self.updateProjectileStats({"gravity":0});
            };
        }

        public function stopX(_arg_1:*=null):*
        {
            this.self.setXSpeed(0);
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.maxLandLoops = 5;
            this.landLoops = 0;
            this.maxMoveLoops = 1;
            this.moveLoops = 0;
            this.fromAir = false;
            if (SSF2API.isReady() && this.self)
            {
                this.owner = this.self.getOwner();
                if (this.owner.getCurrentAttackFrame() == "b_down_air")
                {
                    this.fromAir = true;
                    this.self.setXSpeed(0);
                };
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.ground);
            };
        }

        internal function frame2():*
        {
            if (this.fromAir)
            {
                this.self.stancePlayFrame("airLoop");
            };
        }

        internal function frame4():*
        {
            this.self.stancePlayFrame("potionLoop");
        }

        internal function frame5():*
        {
            this.self.updateProjectileStats({
                "canBePocketed":false,
                "canBeAbsorbed":true
            });
        }

        internal function frame9():*
        {
            this.self.setXSpeed(1, false);
            this.self.playSound("fire");
        }

        internal function frame13():*
        {
            this.self.setXSpeed(3, false);
            this.self.addEventListener(SSF2Event.GROUND_LEAVE, this.stopX);
        }

        internal function frame24():*
        {
            if (this.moveLoops < this.maxMoveLoops)
            {
                this.self.stancePlayFrame("moveLoop");
                this.moveLoops++;
            };
        }

        internal function frame33():*
        {
            this.self.destroy();
        }

        internal function frame43():*
        {
            this.self.attachEffect("dust");
            this.self.destroy();
        }

        internal function frame53():*
        {
            this.self.attachEffect("dust");
            this.self.destroy();
        }

        internal function frame70():*
        {
            this.self.stancePlayFrame("airLoop");
        }

        internal function frame72():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("suspend");
        }

        internal function frame73():*
        {
            this.self = SSF2API.getProjectile(this);
            this.maxLandLoops = 5;
            this.landLoops = 0;
            this.maxMoveLoops = 1;
            this.moveLoops = 0;
            this.fromAir = false;
            if (SSF2API.isReady() && this.self)
            {
                this.owner = this.self.getOwner();
                if (!this.owner.isOnGround())
                {
                    this.fromAir = true;
                    this.self.setXSpeed(0);
                };
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.ground);
            };
        }

        internal function frame74():*
        {
            if (this.fromAir)
            {
                this.self.stancePlayFrame("airLoop");
            }
            else
            {
                this.self.stancePlayFrame("potionLoop");
            };
        }


    }
}

