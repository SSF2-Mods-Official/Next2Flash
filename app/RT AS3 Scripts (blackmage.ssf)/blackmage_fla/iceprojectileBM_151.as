// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//blackmage_fla.iceprojectileBM_151

package blackmage_fla
{
    import flash.display.MovieClip;

    public dynamic class iceprojectileBM_151 extends MovieClip 
    {

        internal var attackBox:MovieClip;
        internal var hitBox:MovieClip;
        internal var self:*;
        internal var isOnGround:Boolean;
        internal var isLeft:Boolean;
        internal var newProjectile:*;
        internal var keepNext:Boolean;
        internal var character:*;

        public function iceprojectileBM_151()
        {
            addFrameScript(0, this.frame1, 1, this.frame2, 3, this.frame4, 8, this.frame9, 9, this.frame10, 16, this.frame17, 20, this.frame21, 25, this.frame26, 26, this.frame27, 27, this.frame28, 28, this.frame29, 29, this.frame30, 31, this.frame32, 32, this.frame33, 34, this.frame35, 51, this.frame52, 52, this.frame53, 55, this.frame56);
        }

        public function toEnd(_arg_1:*):*
        {
            this.self.removeEventListener(SSF2Event.PROJ_DESTROYED, this.toEnd);
            this.self.stancePlayFrame("end");
        }

        public function shieldIt(_arg_1:*):*
        {
            this.flipIt(_arg_1.data.receiver);
        }

        public function reverseIt(_arg_1:*):*
        {
            this.flipIt(_arg_1.data.opponent);
        }

        public function flipIt(_arg_1:*):*
        {
            if (_arg_1.getType() == "SSF2Character")
            {
                this.character = _arg_1;
            };
            this.isLeft = (!(this.isLeft));
            this.self.updateAttackBoxStats(1, {"priority":-1});
            if (((!(this.newProjectile == null)) && (!(this.keepNext))))
            {
                this.newProjectile.destroy();
                this.shootIt();
            };
        }

        public function shootIt():void
        {
            var _local_1:* = this.self.getX();
            var _local_2:* = this.self.getY();
            var _local_3:* = 55;
            if (!this.isOnGround)
            {
                _local_3 = 25;
            };
            if (this.isLeft)
            {
                _local_3 = (_local_3 * -1);
            };
            this.character.fireProjectile(this.self.exportStats(), (_local_1 + _local_3), _local_2, true);
            this.newProjectile = this.character.getCurrentProjectile();
            if (this.isLeft)
            {
                this.newProjectile.stancePlayFrame("left");
            };
        }

        public function killIt():void
        {
            if (((!(this.self.isOnGround())) || (this.self.getGlobalVariable("destroy") == "true")))
            {
                this.self.destroy();
            };
        }

        public function landIt(_arg_1:*):void
        {
            this.self.stancePlayFrame("chibland");
            this.shootIt();
        }

        internal function frame1():*
        {
            var _local_1:MovieClip;
            var _local_2:MovieClip;
            var _local_3:*;
            var _local_4:Boolean;
            var _local_5:Boolean;
            var _local_6:*;
            var _local_7:Boolean;
            var _local_8:*;
            var _local_9:* = 55;
            this.self = SSF2API.getProjectile(this);
            this.isOnGround = true;
            this.isLeft = false;
            this.keepNext = false;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.visible = false;
                if (!this.self.isFacingRight())
                {
                    this.self.updateAttackBoxStats(1, {"direction":95});
                };
                this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.toEnd);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.shieldIt);
                this.self.addEventListener(SSF2Event.REVERSE, this.reverseIt);
            };
        }

        internal function frame2():*
        {
            this.self.createTimer(1, 20, this.killIt, false);
        }

        internal function frame4():*
        {
            if (!this.self.inState(PState.DEAD))
            {
                this.visible = true;
            };
        }

        internal function frame9():*
        {
            SSF2API.getCamera().shake(3);
        }

        internal function frame10():*
        {
            this.self.playSound("iceshoot2");
            this.shootIt();
        }

        internal function frame17():*
        {
            this.keepNext = true;
        }

        internal function frame21():*
        {
            this.self.setXSpeed(0);
            this.self.setYSpeed(0);
            this.self.updateProjectileStats({"maxgravity":0});
        }

        internal function frame26():*
        {
            this.self.destroy();
        }

        internal function frame27():*
        {
            this.self.setGlobalVariable("streamEndProjectile1", true);
            SSF2API.print("Stream 1 down!");
            this.self.destroy();
        }

        internal function frame28():*
        {
            this.self = SSF2API.getProjectile(this);
            this.isOnGround = true;
            this.isLeft = true;
            this.keepNext = false;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.visible = false;
                if (this.self.isFacingRight())
                {
                    this.self.updateAttackBoxStats(1, {"direction":95});
                };
                this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.toEnd);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.shieldIt);
                this.self.addEventListener(SSF2Event.REVERSE, this.reverseIt);
            };
        }

        internal function frame29():*
        {
            this.self.stancePlayFrame("start");
        }

        internal function frame30():*
        {
            if (((!(this.newProjectile == null)) && (!(this.keepNext))))
            {
                this.newProjectile.destroy();
            };
        }

        internal function frame32():*
        {
            if (this.self == null)
            {
                this.self = SSF2API.getProjectile(this);
            };
            this.self.stancePlayFrame("susloop");
        }

        internal function frame33():*
        {
            this.self = SSF2API.getProjectile(this);
            this.isOnGround = true;
            this.isLeft = false;
            this.keepNext = false;
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.character = this.self.getOwner();
                this.isLeft = (!(this.character.isFacingRight()));
                this.self.addEventListener(SSF2Event.ATTACK_HIT_POWER_SHIELD, this.shieldIt);
                this.self.addEventListener(SSF2Event.REVERSE, this.reverseIt);
                if (this.character.isOnGround())
                {
                    this.visible = false;
                    this.self.addEventListener(SSF2Event.PROJ_DESTROYED, this.toEnd);
                }
                else
                {
                    this.isOnGround = false;
                    this.self.updateProjectileStats({
                        "gravity":1,
                        "maxgravity":12
                    });
                    this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.landIt);
                    this.self.stancePlayFrame("chibair");
                };
            };
        }

        internal function frame35():*
        {
            this.self.stancePlayFrame("start");
        }

        internal function frame52():*
        {
            this.self.stancePlayFrame("chibair");
        }

        internal function frame53():*
        {
            this.self.playSound("sfx_icehit_s");
        }

        internal function frame56():*
        {
            this.self.destroy();
        }


    }
}//package blackmage_fla

