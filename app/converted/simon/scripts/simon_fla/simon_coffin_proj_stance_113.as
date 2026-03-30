package simon_fla
{
    import flash.display.MovieClip;
    import flash.geom.Point;

    public dynamic class simon_coffin_proj_stance_113 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var coffinMask:MovieClip;
        public var self:*;
        public var grabbedChars:Array;
        public var grabbedCharCopies:Array;
        public var pullDistance:Number;
        public var PULL_OFFSET_X:Number;
        public var PULL_OFFSET_Y:Number;
        public var PULL_SPEED:Number;
        public var ENABLE_PULL:Boolean;
        public var SHRINK_RATE:Number;
        public var ENABLE_SHRINK:Boolean;
        public var deathTimer:int;
        public var activated:Boolean;
        public var owner:*;

        public function simon_coffin_proj_stance_113()
        {
            super();
            addFrameScript(0, this.frame1, 5, this.frame6, 6, this.frame7, 18, this.frame19, 26, this.frame27, 30, this.frame31, 32, this.frame33, 77, this.frame78);
        }

        public function syncDummyMCPositions():void
        {
            var _local_1:Number = 0.0;
            var _local_2:Number = 0.0;
            var _local_3:MovieClip;
            var _local_4:MovieClip;
            var _local_5:Boolean;
            if (getChildByName("coffinMask") != null)
            {
                _local_3 = (getChildByName("coffinMask") as MovieClip);
                _local_4 = (_local_3.getChildByName("charContainer") as MovieClip);
                if (this.self.getScale().x < 0)
                {
                    _local_1 += ((-(x) + -(_local_3.x)) + _local_4.x);
                    _local_2 += ((-(y) + -(_local_3.y)) + _local_4.y);
                }
                else
                {
                    _local_1 += ((-(x) + -(_local_3.x)) + -(_local_4.x));
                    _local_2 += ((-(y) + -(_local_3.y)) + _local_4.y);
                };
                _local_5 = true;
            };
            for (var _local_6:int = 0; _local_6 < this.grabbedChars.length; _local_6++)
            {
                if ((_local_4 != null) && (this.grabbedCharCopies[_local_6].parent != _local_4))
                {
                    _local_4.addChild(this.grabbedCharCopies[_local_6]);
                };
                if (this.grabbedCharCopies[_local_6].stance)
                {
                    if (this.grabbedCharCopies[_local_6].stance.currentFrame == this.grabbedCharCopies[_local_6].stance.totalFrames)
                    {
                        this.grabbedCharCopies[_local_6].stance.gotoAndStop(1);
                    }
                    else
                    {
                        this.grabbedCharCopies[_local_6].stance.gotoAndStop((this.grabbedCharCopies[_local_6].stance.currentFrame + 1));
                    };
                };
                if (this.grabbedChars[_local_6].getPaletteSwapData() && this.grabbedChars[_local_6].getPaletteSwapData().paletteSwap)
                {
                    SSF2Utils.replacePalette(this.grabbedCharCopies[_local_6], this.grabbedChars[_local_6].getPaletteSwapData().paletteSwap, 3);
                };
                if (_local_5)
                {
                    this.grabbedCharCopies[_local_6].x = _local_1;
                    this.grabbedCharCopies[_local_6].y = _local_2;
                }
                else
                {
                    this.grabbedCharCopies[_local_6].x = this.grabbedChars[_local_6].getX();
                    this.grabbedCharCopies[_local_6].y = this.grabbedChars[_local_6].getY();
                };
            };
        }

        public function cleanupDummyMCs():void
        {
            for (var _local_1:int = 0; _local_1 < this.grabbedChars.length; _local_1++)
            {
                if (this.grabbedCharCopies[_local_1].parent != null)
                {
                    this.grabbedCharCopies[_local_1].parent.removeChild(this.grabbedCharCopies[_local_1]);
                    this.grabbedCharCopies[_local_1] = null;
                };
            };
        }

        public function grabOpponent(_arg_1:*):void
        {
            var _local_2:* = undefined;
            var _local_3:MovieClip;
            var _local_4:Object;
            if (_arg_1.data.receiver.getType() == "SSF2Character")
            {
                _local_2 = _arg_1.data.receiver;
                if (!(_local_2.isDisposed()) && !(_local_2.inState(CState.CAUGHT)))
                {
                    _local_2.grab(this.owner.getUID(), false, false, true);
                    if (_local_2.inState(CState.CAUGHT))
                    {
                        _local_3 = SSF2API.getMCByLinkageName(_local_2.getCharacterStat("linkage_id"));
                        _local_3.gotoAndStop("falling");
                        SSF2Utils.removeFrameScripts(_local_3.stance);
                        _local_3.bypassTicker = true;
                        _local_4 = SSF2API.getCostumeData(_local_2.getCharacterStat("statsName"), ((SSF2API.getGameMode() === GameMode.TRAINING) ? -1 : _local_2.getTeamID()), _local_2.getCostume());
                        SSF2Utils.setColorFilters(_local_3, _local_4);
                        _local_2.getMC().parent.addChild(_local_3);
                        _local_2.setVisibility(false);
                        this.grabbedChars.push(_local_2);
                        this.grabbedCharCopies.push(_local_3);
                        this.syncDummyMCPositions();
                        _local_3.scaleX = _local_2.getMC().scaleX;
                        _local_3.scaleY = _local_2.getMC().scaleY;
                        if (!this.activated)
                        {
                            this.activated = true;
                            this.self.stancePlayFrame("activate");
                            this.self.updateProjectileStats({"time_max":999999});
                            this.self.setXSpeed(0);
                            this.self.createTimer(1, 0, this.timeOut);
                        };
                    };
                };
            };
        }

        public function pullGrabbedOpponents():void
        {
            var _local_2:Number = NaN;
            var _local_3:Number = NaN;
            for (var _local_1:int = 0; _local_1 < this.grabbedChars.length; _local_1++)
            {
                if (this.grabbedChars[_local_1] && !(this.grabbedChars[_local_1].isDisposed()))
                {
                    _local_2 = (((this.self.getX() + this.PULL_OFFSET_X) - this.grabbedChars[_local_1].getX()) / 10);
                    _local_3 = (((this.self.getY() + this.PULL_OFFSET_Y) - this.grabbedChars[_local_1].getY()) / 10);
                    this.grabbedChars[_local_1].safeMove(_local_2, 0);
                    this.grabbedChars[_local_1].safeMove(0, _local_3);
                    this.syncDummyMCPositions();
                };
            };
        }

        public function shrinkGrabbedOpponents():void
        {
            if (!this.ENABLE_SHRINK)
            {
                return;
            };
            for (var _local_1:int = 0; _local_1 < this.grabbedChars.length; _local_1++)
            {
                this.grabbedCharCopies[_local_1].scaleX = (this.grabbedCharCopies[_local_1].scaleX * this.SHRINK_RATE);
                this.grabbedCharCopies[_local_1].scaleY = (this.grabbedCharCopies[_local_1].scaleY * this.SHRINK_RATE);
            };
        }

        public function pullNearbyOpponents():void
        {
            var _local_3:Point;
            var _local_4:Point;
            var _local_5:Number = NaN;
            var _local_6:Number = NaN;
            var _local_7:Number = NaN;
            if (!this.ENABLE_PULL)
            {
                return;
            };
            var _local_1:Array = SSF2API.getCharacters();
            for (var _local_2:int = 0; _local_2 < _local_1.length; _local_2++)
            {
                if (_local_1[_local_2] && (_local_1[_local_2].getUID() != this.owner.getUID()) && !(_local_1[_local_2].isDisposed()) && !(_local_1[_local_2].inState(CState.CAUGHT)) && !(_local_1[_local_2].inState(CState.BARREL)) && !(_local_1[_local_2].inState(CState.STAR_KO)) && !(_local_1[_local_2].inState(CState.SCREEN_KO)) && !(_local_1[_local_2].inState(CState.REVIVAL)) && !(_local_1[_local_2].inState(CState.LEDGE_CLIMB)) && !(_local_1[_local_2].inState(CState.LEDGE_HANG)) && !(_local_1[_local_2].inState(CState.LEDGE_ROLL)) && !(_local_1[_local_2].inState(CState.PITFALL)) && !(_local_1[_local_2].isStandby()))
                {
                    _local_3 = new Point(_local_1[_local_2].getX(), _local_1[_local_2].getY());
                    _local_4 = new Point(this.self.getX(), this.self.getY());
                    if (Point.distance(_local_3, _local_4) < this.pullDistance)
                    {
                        _local_5 = SSF2Utils.getAngleBetween(_local_4, _local_3);
                        _local_6 = -(SSF2Utils.calculateXSpeed(this.PULL_SPEED, _local_5));
                        _local_7 = SSF2Utils.calculateYSpeed(this.PULL_SPEED, _local_5);
                        _local_1[_local_2].safeMove(_local_6, 0);
                        _local_1[_local_2].safeMove(0, _local_7);
                    };
                };
            };
        }

        public function timeOut():void
        {
            this.deathTimer--;
            if (this.deathTimer <= 0)
            {
                this.self.destroy();
            };
        }

        internal function frame1():*
        {
            this.self = SSF2API.getProjectile(this);
            this.grabbedChars = [];
            this.grabbedCharCopies = [];
            this.pullDistance = 125;
            this.PULL_OFFSET_X = 0;
            this.PULL_OFFSET_Y = 0;
            this.PULL_SPEED = 12;
            this.ENABLE_PULL = false;
            this.SHRINK_RATE = 0.9;
            this.ENABLE_SHRINK = true;
            this.deathTimer = (30 * 2);
            this.activated = false;
            if (SSF2API.isReady() && this.self)
            {
                this.owner = this.self.getOwner();
                this.self.addEventListener(SSF2Event.ATTACK_CONNECT, this.grabOpponent);
                this.self.addEventListener(SSF2Event.ATTACK_HIT_SHIELD, this.grabOpponent);
                this.self.createTimer(1, 0, this.pullNearbyOpponents);
                SSF2API.playSound("ssf2_snd_sfx_simon_final_00");
                this.self.addToCamera();
            };
        }

        internal function frame6():*
        {
            if (this.grabbedChars.length <= 0)
            {
                this.self.stancePlayFrame("fail");
            };
        }

        internal function frame7():*
        {
            this.pullDistance *= 1.5;
            this.self.updateProjectileStats({
                "xspeed":0,
                "xdecay":null
            });
            SSF2API.playSound("megaman_final_smash_02");
        }

        internal function frame19():*
        {
            this.self.createTimer(1, 0, this.pullGrabbedOpponents);
        }

        internal function frame27():*
        {
            this.self.createTimer(1, 0, this.shrinkGrabbedOpponents);
        }

        internal function frame31():*
        {
            this.self.destroyTimer(this.pullGrabbedOpponents);
            this.self.destroyTimer(this.shrinkGrabbedOpponents);
            SSF2API.playSound("ssf2_snd_sfx_simon_final_02");
            this.cleanupDummyMCs();
        }

        internal function frame33():*
        {
            this.owner.triggerFSCutscene();
            this.self.destroy();
        }

        internal function frame78():*
        {
            this.self.destroy();
        }


    }
}

