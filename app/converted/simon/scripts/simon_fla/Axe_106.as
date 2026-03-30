package simon_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class Axe_106 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var self:*;

        public function Axe_106()
        {
            super();
            addFrameScript(0, this.frame1, 17, this.frame18, 38, this.frame39, 59, this.frame60, 80, this.frame81, 81, this.frame82, 82, this.frame83, 83, this.frame84, 84, this.frame85);
        }

        public function ground(_arg_1:*=null):*
        {
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.ground);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.wall);
            this.self.destroyTimer(this.afterImage);
            this.self.updateAttackBoxStats(1, {
                "hitStun":4,
                "selfHitStun":4
            });
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.playSound("brawl_kick_m");
            SSF2API.getCamera().shake(6);
            this.self.stancePlayFrame("land");
        }

        public function wall(_arg_1:*=null):*
        {
            if (SSF2API.getPlatformBetweenPoints(new Point(this.self.getX(), (this.self.getY() - 30)), new Point(this.self.getX(), (this.self.getY() - 40)), {"ignoreFallthrough":true}))
            {
                if (this.self.getYSpeed() < -12)
                {
                    this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.ground);
                    this.self.removeEventListener(SSF2Event.HIT_WALL, this.wall);
                    this.self.destroyTimer(this.afterImage);
                    this.self.updateProjectileStats({"gravity":0});
                    this.self.updateAttackBoxStats(1, {
                        "hitStun":4,
                        "selfHitStun":4
                    });
                    this.self.setXSpeed(0);
                    this.self.setYSpeed(0);
                    this.self.playSound("brawl_kick_m");
                    SSF2API.getCamera().shake(6);
                    this.self.stancePlayFrame("roof");
                };
            }
            else
            {
                this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.ground);
                this.self.removeEventListener(SSF2Event.HIT_WALL, this.wall);
                this.self.destroyTimer(this.afterImage);
                this.self.updateProjectileStats({"gravity":0});
                this.self.updateAttackBoxStats(1, {
                    "hitStun":4,
                    "selfHitStun":4
                });
                this.self.setXSpeed(0);
                this.self.setYSpeed(0);
                this.self.playSound("brawl_kick_m");
                SSF2API.getCamera().shake(6);
                this.self.stancePlayFrame("wall");
            };
        }

        public function afterImage():void
        {
            var _local_1:* = undefined;
            if (!this.self.inState(PState.DEAD))
            {
                _local_1 = this.self.applyPalette(this.self.attachEffect("AxeWind", {"behind":true}));
            };
        }

        public function destroy(_arg_1:*=null):*
        {
            this.self.attachEffect("dust");
            this.self.destroy();
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.ground);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wall);
                this.self.createTimer(4, 0, this.afterImage);
            };
        }

        internal function frame18():*
        {
            this.self.stancePlayFrame("loop");
        }

        internal function frame39():*
        {
            this.destroy();
        }

        internal function frame60():*
        {
            this.destroy();
        }

        internal function frame81():*
        {
            this.destroy();
        }

        internal function frame82():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.destroyTimer(this.afterImage);
        }

        internal function frame83():*
        {
            this.self.stancePlayFrame("suspend");
        }

        internal function frame84():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.ground);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.wall);
                this.self.createTimer(4, 0, this.afterImage);
            };
        }

        internal function frame85():*
        {
            this.self.stancePlayFrame("loop");
        }


    }
}

