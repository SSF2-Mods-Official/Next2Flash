package dedede_fla
{
    import flash.display.MovieClip;
    import flash.events.Event;

    public dynamic class ddd_bigMissile_283 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var attackBox3:MovieClip;
        public var hitBox:MovieClip;
        public var homing:MovieClip;
        public var self:*;

        public function ddd_bigMissile_283()
        {
            super();
            addFrameScript(0, this.frame1, 64, this.frame65, 69, this.frame70, 70, this.frame71, 71, this.frame72, 72, this.frame73, 73, this.frame74);
        }

        public function jumpToContinue(_arg_1:Event=null):*
        {
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.jumpToContinue);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.jumpToDieWall);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.jumpToContinue);
            this.self.destroyTimer(this.setHomingSpeed);
            this.self.stancePlayFrame("continue");
        }

        public function jumpToDieWall(_arg_1:Event=null):*
        {
            this.self.removeEventListener(SSF2Event.ATTACK_CONNECT, this.jumpToContinue);
            this.self.removeEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
            this.self.removeEventListener(SSF2Event.HIT_WALL, this.jumpToDieWall);
            this.self.removeEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.jumpToContinue);
            this.self.destroyTimer(this.setHomingSpeed);
            this.self.stancePlayFrame("continue");
        }

        public function setHomingSpeed():*
        {
            var _local_1:* = Math.sqrt((Math.pow(this.self.getXSpeed(), 2) + Math.pow(this.self.getYSpeed(), 2)));
            if (_local_1 <= 2)
            {
                this.jumpToContinue();
            };
            this.self.updateProjectileStats({"homingSpeed":_local_1});
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.jumpToContinue);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.jumpToDieWall);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.jumpToContinue);
                this.self.createTimer(1, 0, this.setHomingSpeed);
            };
        }

        internal function frame65():*
        {
            SSF2API.getCamera().shake(8);
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.updateProjectileStats({"trailEffect":null});
            this.self.attachEffectOverlay("explosion_air", {
                "x":12,
                "scaleX":1.75,
                "scaleY":1.75
            });
        }

        internal function frame70():*
        {
            this.self.destroy();
        }

        internal function frame71():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.updateProjectileStats({"trailEffect":null});
        }

        internal function frame72():*
        {
            this.self.stancePlayFrame("suspend");
        }

        internal function frame73():*
        {
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.self.updateProjectileStats({"trailEffect":"missileTrail"});
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.jumpToContinue);
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.jumpToContinue);
                this.self.addEventListener(SSF2Event.HIT_WALL, this.jumpToDieWall);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.jumpToContinue);
                this.self.createTimer(1, 0, this.setHomingSpeed);
            };
        }

        internal function frame74():*
        {
            this.self.stancePlayFrame("start");
        }


    }
}

